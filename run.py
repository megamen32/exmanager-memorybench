#!/usr/bin/env python3
"""Run a native backend against explicit local fixtures in a separate experiment namespace."""
from __future__ import annotations
import argparse,fcntl,json,os,subprocess,sys,uuid
from pathlib import Path
from benchlib import fingerprint,read_jsonl,validate
HERE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('arm',choices=['rag','hindsight','mem0','graphiti','graphiti-combined'])
 p.add_argument('--events',type=Path,default=HERE/'examples/synthetic/events.jsonl')
 p.add_argument('--cases',type=Path,default=HERE/'examples/synthetic/cases.jsonl')
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--model',default=os.getenv('MEMBENCH_MODEL'))
 p.add_argument('--context-tokens',type=int,default=1536)
 p.add_argument('--query-time',default='2026-10-17T00:00:00Z')
 p.add_argument('--validate-only',action='store_true')
 p.add_argument('--read-only',action='store_true',help='Fresh queries, no source re-ingestion')
 args=p.parse_args();events=read_jsonl(args.events);cases=read_jsonl(args.cases)
 validate(events,cases,args.query_time)
 if args.validate_only:
  print(json.dumps({'valid':True,'events':len(events),'cases':len(cases)}));return 0
 if not args.model:p.error('Choose --model or MEMBENCH_MODEL; use an explicit model, not a fallback combo')
 if not 128<=args.context_tokens<=65536:p.error('Context cap must be 128..65536')
 root=args.output.resolve();root.mkdir(parents=True,exist_ok=True);os.chmod(root,0o700)
 code={str(x.relative_to(HERE)):x.read_text() for x in [HERE/'benchlib.py',HERE/'run.py',HERE/'src/benchmark.py']}
 signature=fingerprint({'events':events,'cases':cases,'model':args.model,'cap':args.context_tokens,'query_time':args.query_time,'embedding':os.getenv('MEMBENCH_EMBED_MODEL','sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'),'dimension':os.getenv('MEMBENCH_EMBED_DIM','384'),'code':fingerprint(code)})
 with (root/'run.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  path=root/'manifest.json'
  if path.exists():
   manifest=json.loads(path.read_text())
   if manifest['signature']!=signature:raise ValueError('Inputs, configuration or source changed; use a NEW output directory')
  else:
   if args.read_only:raise ValueError('Read-only requires an existing run')
   manifest={'signature':signature,'namespace':uuid.uuid4().hex,'model':args.model,'dataset_sha256':fingerprint(events),'context_tokens':args.context_tokens,'query_time':args.query_time,'note':'Public runner experiment, not the private calibration'}
   path.write_text(json.dumps(manifest,indent=2))
  (root/'data').mkdir(exist_ok=True);(root/'results').mkdir(exist_ok=True)
  for name,items in [('events',events),('cases',cases)]:
   (root/'data'/f'{name}.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in items)+'\n')
  env=os.environ.copy()
  env.update(MEMBENCH_ROOT=str(root),MEMBENCH_MODEL=args.model,MEMBENCH_NAMESPACE=manifest['namespace'],MEMBENCH_QUERY_TIME=args.query_time,MEMBENCH_CONTEXT_TOKENS=str(args.context_tokens),PYTHONUNBUFFERED='1',MEM0_TELEMETRY='false',GRAPHITI_TELEMETRY_ENABLED='false',PYTHONPATH=str(HERE)+os.pathsep+str(HERE/'src'))
  if args.read_only:env['MEMBENCH_READ_ONLY']='1'
  else:env.pop('MEMBENCH_READ_ONLY',None)
  if args.arm=='graphiti-combined' and not (root/'results/graphiti/ingestion.json').exists():raise ValueError('Run graphiti first with the same output directory')
  return subprocess.run([sys.executable,str(HERE/'src/benchmark.py'),args.arm],env=env,timeout=3600).returncode
if __name__=='__main__':
 try:raise SystemExit(main())
 except (ValueError,BlockingIOError,subprocess.TimeoutExpired) as error:
  print('Run refused:',type(error).__name__,str(error),file=sys.stderr);raise SystemExit(2)
