import unittest
from src.v761 import build_investigation,to_markdown,query_for_sources
from src.engine import integrity

UNAVAILABLE={'pubmed':{'status':'UNAVAILABLE','records':[],'error':'software-only test: unavailable'},'trials':{'status':'UNAVAILABLE','records':[],'error':'software-only test: unavailable'}}
NOT_REQUESTED={'pubmed':{'status':'NOT_REQUESTED','records':[]},'trials':{'status':'NOT_REQUESTED','records':[]}}
Q='Investigate the clinical evidence, population characteristics, and potential treatment opportunity for finerenone (Kerendia) in patients with chronic kidney disease and type 2 diabetes.'
class IntegrationTests(unittest.TestCase):
 def test_immutable_baseline(self):self.assertEqual(integrity()['baseline_sha256'],'4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf')
 def test_partial_answer_preserved(self):
  b=build_investigation(Q,external_results=UNAVAILABLE)
  self.assertEqual(b['status'],'PARTIAL_ANSWER_WITH_GUARDS')
  self.assertTrue(any('9,233,798' in s['text'] for s in b['sections']))
  self.assertTrue(any('DR6' in s['text'] or 'DR7' in s['text'] for s in b['sections']))
  self.assertTrue(any('UNAVAILABLE' in s['text'] for s in b['sections']))
  self.assertTrue(any(c['type']=='NHANES observation' for c in b['citations']))
 def test_no_fabricated_ids(self):
  b=build_investigation(Q,external_results=UNAVAILABLE)
  self.assertFalse(any(c['type'] in ('pubmed','trials') for c in b['citations']))
 def test_trends_block_only_claim(self):
  b=build_investigation('Did CKD population increase across cycles in NHANES?',external_results=NOT_REQUESTED)
  self.assertEqual(b['status'],'PARTIAL_ANSWER_WITH_GUARDS')
  self.assertTrue(any('trend' in w.lower() for w in b['warnings']))
 def test_report_source_ids(self):
  b=build_investigation(Q,external_results=NOT_REQUESTED)
  m=to_markdown(b)
  self.assertIn('NHANES_2021_2023_PRIMARY',m)
  self.assertIn('V7.6.1',m)
 def test_actual_record_injection_is_traceable(self):
  # Isolated software fixture; identifiers below are intentionally invalid and never written to evidence files.
  records={'pubmed':{'status':'RETRIEVED','retrieved_utc':'software-test-only','records':[{'pmid':'TEST-ONLY','title':'TEST ONLY','url':'https://pubmed.ncbi.nlm.nih.gov/TEST-ONLY/'}]},'trials':{'status':'NOT_REQUESTED','records':[]}}
  b=build_investigation('finerenone evidence',external_results=records)
  self.assertTrue(any(c['id']=='TEST-ONLY' for c in b['citations']))
  self.assertEqual(b['citations'][-1]['verification'],'RETRIEVED_NOT_CRITICALLY_APPRAISED')
 def test_kg_baseline_classification(self):
  b=build_investigation('finerenone kidney disease',external_results=NOT_REQUESTED)
  self.assertTrue(any(c['verification']=='BASELINE_INTEGRITY_ONLY' for c in b['citations']))
 def test_live_opt_out(self):
  b=build_investigation('finerenone evidence',fetch_live=False)
  self.assertEqual(b['external']['pubmed']['status'],'NOT_REQUESTED')
 def test_source_query(self):self.assertIn('finerenone',query_for_sources(Q))
if __name__=='__main__':unittest.main()
