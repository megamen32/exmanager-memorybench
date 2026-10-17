"""Local OpenAI-compatible gateway. Usage ledger excludes prompts and credentials."""
from __future__ import annotations
import asyncio,base64,json,os,re,time
from contextlib import asynccontextmanager
from pathlib import Path
import httpx,numpy as np
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
MODEL=os.getenv('MEMBENCH_MODEL','');UPSTREAM=os.getenv('UPSTREAM_BASE_URL','').rstrip('/');KEY=os.getenv('UPSTREAM_API_KEY','')
EMBED=os.getenv('MEMBENCH_EMBED_MODEL','sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
ROOT=Path(os.getenv('MEMBENCH_GATEWAY_DATA','.runs/gateway'));ROOT.mkdir(parents=True,exist_ok=True);os.chmod(ROOT,0o700)
LEDGER=ROOT/'calls.jsonl';MAX_CALLS=int(os.getenv('MEMBENCH_MAX_CALLS','600'));MAX_TOKENS=int(os.getenv('MEMBENCH_MAX_TOKENS','1500000'))
llm_lock=asyncio.Lock();embed_lock=asyncio.Lock();counts={'calls':0,'tokens':0};embedder=None
if LEDGER.exists():
 for line in LEDGER.read_text().splitlines():
  row=json.loads(line)
  if row.get('kind')=='llm':counts['calls']+=1;counts['tokens']+=(row.get('usage') or {}).get('total_tokens',0) or 0

def record(value):
 with LEDGER.open('a',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False)+'\n')
def check_arm(arm):
 if not re.fullmatch(r'[a-z0-9-]{1,80}',arm):raise HTTPException(400,'Invalid experiment label')
@asynccontextmanager
async def lifespan(app):
 global embedder
 if not MODEL or not UPSTREAM or not KEY or KEY=='replace-locally':raise RuntimeError('Configure upstream URL, model and API key locally')
 from fastembed import TextEmbedding
 embedder=await asyncio.to_thread(TextEmbedding,model_name=EMBED,cache_dir=str(ROOT/'model-cache'),threads=2)
 yield
app=FastAPI(lifespan=lifespan)
@app.get('/health')
async def health():return {'ready':embedder is not None,'model':MODEL,'embedding_model':EMBED,'usage':counts}
async def body(request):
 raw=await request.body()
 if len(raw)>2*1024*1024:raise HTTPException(413,'Request too large')
 try:result=json.loads(raw)
 except ValueError:raise HTTPException(400,'Invalid JSON')
 if not isinstance(result,dict):raise HTTPException(400,'Expected object')
 return result
@app.post('/{arm}/v1/embeddings')
async def embeddings(arm:str,request:Request):
 check_arm(arm);data=await body(request);texts=data.get('input');texts=[texts] if isinstance(texts,str) else texts
 if not isinstance(texts,list) or not 1<=len(texts)<=256 or not all(isinstance(t,str) and len(t)<=100000 for t in texts):raise HTTPException(400,'Expected bounded strings')
 started=time.monotonic()
 async with embed_lock:vectors=await asyncio.to_thread(lambda:list(embedder.embed(texts,batch_size=16)))
 items=[]
 for i,vector in enumerate(vectors):
  value=base64.b64encode(np.asarray(vector,dtype='<f4').tobytes()).decode() if data.get('encoding_format')=='base64' else vector.tolist()
  items.append({'object':'embedding','index':i,'embedding':value})
 record({'kind':'embedding','arm':arm,'items':len(texts),'seconds':time.monotonic()-started})
 return {'object':'list','data':items,'model':EMBED,'usage':{'prompt_tokens':0,'total_tokens':0}}
@app.post('/{arm}/v1/chat/completions')
async def chat(arm:str,request:Request):
 check_arm(arm);data=await body(request)
 if data.get('stream'):raise HTTPException(400,'Streaming disabled')
 async with llm_lock:
  if counts['calls']>=MAX_CALLS or counts['tokens']>=MAX_TOKENS:raise HTTPException(429,'Experiment limit reached')
  counts['calls']+=1;data['model']=MODEL;data['stream']=False;data['temperature']=0
  data['max_tokens']=min(int(data.get('max_tokens') or data.pop('max_completion_tokens',8192)),8192);data.pop('max_completion_tokens',None)
  if os.getenv('MEMBENCH_DISABLE_THINKING','false').lower()=='true':data['thinking']={'type':'disabled'}
  started=time.monotonic()
  try:
   async with httpx.AsyncClient(timeout=150,trust_env=False) as upstream:response=await upstream.post(UPSTREAM+'/chat/completions',json=data,headers={'Authorization':'Bearer '+KEY})
   if not response.is_success:
    record({'kind':'llm','arm':arm,'status':response.status_code,'seconds':time.monotonic()-started})
    return JSONResponse({'error':{'message':'Upstream request failed; no body logged'}},status_code=response.status_code)
   payload=response.json();usage=payload.get('usage') or {};counts['tokens']+=usage.get('total_tokens',0) or 0
   record({'kind':'llm','arm':arm,'status':response.status_code,'model':payload.get('model'),'usage':usage,'seconds':time.monotonic()-started});return payload
  except Exception as error:
   record({'kind':'llm','arm':arm,'status':502,'error':type(error).__name__,'seconds':time.monotonic()-started})
   return JSONResponse({'error':{'message':type(error).__name__}},status_code=502)
