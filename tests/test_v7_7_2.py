import unittest
from unittest.mock import patch
from src.v772 import build_v772,classify_intent,to_markdown

Q='How many US adults meet the CKD laboratory-screening and probable T2D criteria in NHANES 2021–2023? Report prevalence, confidence interval, survey weights and unweighted cases; distinguish this from finerenone treatment eligibility.'
class V772Tests(unittest.TestCase):
 def test_intent_population_even_with_finerenone_eligibility_disclaimer(self):
  self.assertEqual(classify_intent(Q),'POPULATION_ONLY')
 def test_integrated_intent(self):
  self.assertEqual(classify_intent('Investigate the clinical evidence, population characteristics, and potential treatment opportunity for finerenone'),'INTEGRATED')
 def test_population_no_external_calls(self):
  with patch('src.v772.build_v77',side_effect=AssertionError('Must not invoke full pipeline')):
   b=build_v772(Q,fetch_live=True)
  self.assertEqual(b['intent'],'POPULATION_ONLY')
  self.assertEqual(b['external']['pubmed']['status'],'NOT_REQUESTED')
  self.assertEqual(b['technical_trace']['clinical_kg_lexical_retrieval'],[])
  self.assertEqual(len(b['sections']),2)
 def test_report_fidelity(self):
  b=build_v772(Q,fetch_live=False);t=to_markdown(b)
  for term in ('9,233,798','4.2009%','7,843,384','10,624,212','WTPH2YR','283','5,143','NHANES_2021_2023_PRIMARY','not confirmed','V7.7.2'):
   self.assertIn(term,t)
  for term in ('## Clinical knowledge graph context','## Authentic external evidence','## Targeted pivotal evidence'):
   self.assertNotIn(term,t)
 def test_preserved_integrity(self):
  self.assertEqual(build_v772(Q,fetch_live=False)['technical_trace']['baseline_integrity']['baseline_sha256'],'4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf')
