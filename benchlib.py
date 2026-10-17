"""Validation and grading helpers. No engine dependencies or network calls."""
from __future__ import annotations
import hashlib,json,re
from datetime import datetime
from pathlib import Path
IDENTIFIER=re.compile(r'^[a-zA-Z0-9_-]{1,100}$')
def read_jsonl(path):
 rows=[]
 with Path(path).open(encoding='utf-8') as f:
  for line in f:
   if not line.strip():continue
   row=json.loads(line)
   if not isinstance(row,dict):raise ValueError('Expected JSON objects')
   rows.append(row)
 if not rows:raise ValueError('Input is empty')
 return rows
def timestamp(value):
 result=datetime.fromisoformat(value.replace('Z','+00:00'))
 if result.utcoffset() is None:raise ValueError('Timestamp requires UTC offset')
 return result
def validate(events,cases,query_time):
 ids=set();anchor=timestamp(query_time);previous=None
 for event in events:
  for key in ('id','scope','at','origin','text'):
   if not isinstance(event.get(key),str) or not event[key].strip():raise ValueError('Missing event field '+key)
  if not IDENTIFIER.fullmatch(event['id']) or not IDENTIFIER.fullmatch(event['scope']):raise ValueError('Unsafe event identifier')
  if event['id'] in ids:raise ValueError('Duplicate event id')
  ids.add(event['id']);when=timestamp(event['at'])
  if when>anchor:raise ValueError('Future evidence')
  if previous is not None and when<previous:raise ValueError('Events must be chronological')
  previous=when
 mapping={e['id']:e for e in events};case_ids=set()
 for case in cases:
  if not IDENTIFIER.fullmatch(case.get('id','')) or case['id'] in case_ids:raise ValueError('Unsafe or duplicate case id')
  case_ids.add(case['id'])
  if not isinstance(case.get('q'),str) or not case['q'].strip():raise ValueError('Missing question')
  if not isinstance(case.get('gold'),dict) or not case['gold']:raise ValueError('Missing expected fields')
  if not isinstance(case.get('evidence'),list):raise ValueError('Missing evidence list')
  scope=case.get('scope','owner')
  if not IDENTIFIER.fullmatch(scope):raise ValueError('Unsafe scope')
  for sid in case['evidence']:
   if sid not in mapping:raise ValueError('Unknown evidence id')
   if mapping[sid]['scope']!=scope:raise ValueError('Expected evidence in another scope')
  if not all(isinstance(x,str) and x for x in case.get('forbidden_markers',[])):raise ValueError('Invalid markers')
def fingerprint(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def strict_equal(actual,expected):
 if type(actual) is not type(expected):return False
 if isinstance(expected,dict):return actual.keys()==expected.keys() and all(strict_equal(actual[k],v) for k,v in expected.items())
 if isinstance(expected,list):return len(actual)==len(expected) and all(strict_equal(a,b) for a,b in zip(actual,expected))
 return actual==expected
def grade(case,response,packed,retrieved):
 answer=response.get('answer');answer=answer if isinstance(answer,dict) else {}
 fields={k:k in answer and strict_equal(answer[k],v) for k,v in case['gold'].items()}
 citations=response.get('source_ids',[]);ok=isinstance(citations,list) and all(isinstance(x,str) for x in citations)
 valid={s for row in packed for s in row.get('source_ids',[]) if isinstance(s,str)}
 expected=set(case['evidence'])
 present=ok and (bool(set(citations)&expected) if expected else not citations)
 text=json.dumps({'retrieved':retrieved,'response':response},ensure_ascii=False,default=str)
 return {'field_pass':fields,'answer_pass':all(fields.values()),'citation_valid':ok and all(s in valid for s in citations),'cited_required_evidence':present,'scope_leak':any(x in text for x in case.get('forbidden_markers',[]))}
