import unittest
from src.demo import SAFE_QUESTIONS,observations,graph_neighborhood,evidence_bundle,report_markdown
from src.engine import integrity
from src.v7 import concept_search,investigate
class DemoTests(unittest.TestCase):
 def test_baseline(self):
  d=integrity();self.assertEqual((d['nodes'],d['edges'],d['observations']),(293,517,4))
 def test_real_observations(self):
  o=observations();self.assertEqual(len(o),4);self.assertEqual(next(x for x in o if x['period']=='2021-2023' and x['scenario']=='primary')['survey_weight'],'WTPH2YR')
 def test_lexical_on_actual_list_nodes(self):self.assertTrue(concept_search('kidney disease'))
 def test_graph_actual_edges(self):
  g=graph_neighborhood('kidney');self.assertTrue(g['nodes']);self.assertTrue(g['edges']);self.assertFalse(g['clinical_equivalence_approved'])
 def test_eligibility_block(self):self.assertEqual(investigate('How many people are eligible for Kerendia?')['overall_status'],'BLOCKED')
 def test_trend_block(self):self.assertEqual(investigate('Did the CKD population increase across NHANES cycles?')['overall_status'],'BLOCKED')
 def test_market_block(self):self.assertEqual(investigate('Estimate the addressable market for finerenone')['overall_status'],'BLOCKED')
 def test_report_identifiers(self):
  b=evidence_bundle(SAFE_QUESTIONS[0]);self.assertTrue(b['citations']);self.assertIn(b['citations'][0]['evidence_id'],report_markdown(b))
 def test_no_fake_external(self):
  b=evidence_bundle('Find PubMed trials',live=False);self.assertEqual(b['external']['pubmed']['status'],'NOT_REQUESTED');self.assertFalse(any(c['kind']=='pubmed' for c in b['citations']))
 def test_demo_questions(self):
  for q in SAFE_QUESTIONS:self.assertTrue(evidence_bundle(q)['sections'])
if __name__=='__main__':unittest.main()
