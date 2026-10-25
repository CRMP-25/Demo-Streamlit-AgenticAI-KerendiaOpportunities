import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.engine import load,ask,integrity,EXPECTED_SHA
class Regression(unittest.TestCase):
 def test_baseline(self):
  d=integrity();self.assertEqual(d['baseline_sha256'],EXPECTED_SHA);self.assertEqual(d['nodes'],293);self.assertEqual(d['edges'],517)
 def test_observations(self):self.assertEqual(integrity()['observations'],4)
 def test_links(self):self.assertEqual(integrity()['links'],88)
 def test_population(self):
  a=ask('How many adults have CKD and diabetes?');self.assertEqual(a['status'],'SCREENING_ESTIMATE_WITH_CAVEATS');self.assertEqual(a['evidence_ids'],['NHANES_2021_2023_PRIMARY'])
 def test_other_period(self):self.assertEqual(ask('NHANES 2015-2016 CKD')['evidence_ids'],['NHANES_2015_2016_PRIMARY'])
 def test_eligibility(self):self.assertEqual(ask('How many are eligible for Kerendia?')['status'],'BLOCKED_ELIGIBILITY')
 def test_market(self):self.assertEqual(ask('What is the addressable market size?')['status'],'BLOCKED_ELIGIBILITY')
 def test_trend(self):self.assertEqual(ask('What is the CKD trend?')['status'],'BLOCKED_TREND')
 def test_unknown(self):self.assertEqual(ask('What is the population of Mars?')['status'],'OUT_OF_SCOPE')
 def test_no_approved_links(self):
  d=load();self.assertTrue(all('APPROVED' not in str(x.get('human_review_status','')).upper() for x in d['links']))
if __name__=='__main__':unittest.main()
