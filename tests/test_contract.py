import copy,unittest
from pathlib import Path
from benchlib import grade,read_jsonl,strict_equal,validate,fingerprint
ROOT=Path(__file__).resolve().parents[1]
class ContractTests(unittest.TestCase):
 def setUp(self):self.events=read_jsonl(ROOT/'examples/synthetic/events.jsonl');self.cases=read_jsonl(ROOT/'examples/synthetic/cases.jsonl')
 def test_synthetic_valid(self):validate(self.events,self.cases,'2026-10-17T00:00:00Z')
 def test_smoke_valid(self):validate(read_jsonl(ROOT/'examples/smoke/events.jsonl'),read_jsonl(ROOT/'examples/smoke/cases.jsonl'),'2026-10-17T00:00:00Z')
 def test_future_refused(self):
  with self.assertRaises(ValueError):validate(self.events,self.cases,'2026-10-01T00:00:00Z')
 def test_timezone_required(self):
  self.events[0]['at']='2026-10-01T00:00:00'
  with self.assertRaises(ValueError):validate(self.events,self.cases,'2026-10-17T00:00:00Z')
 def test_duplicate_refused(self):
  self.events[1]['id']=self.events[0]['id']
  with self.assertRaises(ValueError):validate(self.events,self.cases,'2026-10-17T00:00:00Z')
 def test_unsafe_id_refused(self):
  self.cases[0]['id']='../unexpected'
  with self.assertRaises(ValueError):validate(self.events,self.cases,'2026-10-17T00:00:00Z')
 def test_unknown_evidence_refused(self):
  self.cases[0]['evidence']=['invented']
  with self.assertRaises(ValueError):validate(self.events,self.cases,'2026-10-17T00:00:00Z')
 def test_cross_scope_gold_refused(self):
  self.cases[0]['evidence']=['private-control']
  with self.assertRaises(ValueError):validate(self.events,self.cases,'2026-10-17T00:00:00Z')
 def test_bool_is_not_int(self):self.assertFalse(strict_equal(True,1));self.assertFalse(strict_equal(1.0,1));self.assertTrue(strict_equal(False,False))
 def test_missing_null_is_failure(self):self.assertFalse(grade({'gold':{'time':None},'evidence':[]},{'answer':{}},[],[])['answer_pass'])
 def test_malformed_citation_is_failure(self):self.assertFalse(grade({'gold':{'ok':True},'evidence':['e1']},{'answer':{'ok':True},'source_ids':'e1'},[{'source_ids':['e1']}],[])['citation_valid'])
 def test_fabricated_citation_is_failure(self):self.assertFalse(grade({'gold':{'ok':True},'evidence':['e1']},{'answer':{'ok':True},'source_ids':['invented']},[{'source_ids':['e1']}],[])['citation_valid'])
 def test_citation_not_entailment(self):self.assertTrue(grade({'gold':{'ok':True},'evidence':['e1']},{'answer':{'ok':True},'source_ids':['e1']},[{'source_ids':['e1'],'text':'irrelevant'}],[])['citation_valid'])
 def test_leak_checked_before_packing(self):self.assertTrue(grade({'gold':{'project':None},'evidence':[],'forbidden_markers':['SECRET-SYNTHETIC']},{'answer':{'project':None}},[],[{'text':'SECRET-SYNTHETIC'}])['scope_leak'])
 def test_fingerprint_changes(self):
  a=fingerprint(self.events);b=copy.deepcopy(self.events);b[0]['text']+=' changed';self.assertNotEqual(a,fingerprint(b))
if __name__=='__main__':unittest.main()
