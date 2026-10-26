import unittest
from src.v774 import verify_primary_candidate, kg_node_map, readable_graph_v774, build_v774, quantitative_source_findings
from src.version import APP_VERSION, download_name

class TestV774(unittest.TestCase):
 def test_version(self):
  self.assertEqual(APP_VERSION,'V7.7.5')
  self.assertEqual(download_name('Investigation','md'),'Healthcare_Intelligence_Investigation_V7_7_5.md')
 def test_title_verification_fail_closed(self):
  self.assertIsNone(verify_primary_candidate('FIDELIO-DKD','33264825','Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes',{'title':'Unrelated publication'}))
  self.assertIsNotNone(verify_primary_candidate('FIDELIO-DKD','33264825','Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes',{'title':'Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes.'}))
 def test_actual_kg_schema(self):
  nodes=kg_node_map()
  self.assertIn('D34',nodes)
  self.assertIn('diabetes',nodes['D34']['description'].lower())
  readable=readable_graph_v774({'graph_edges':[{'source':'D34','target':'DR16','relation':'is treated by'}]})
  self.assertIn('diabetes',readable.lower())
  self.assertNotIn('**D34**',readable)
 def test_quantitative_no_invention(self):
  self.assertEqual(quantitative_source_findings({'abstract_sections':[{'label':'Results','text':'No effect measures reported.'}]}),[])
 def test_population_preserved(self):
  b=build_v774('How many US adults meet the CKD screening and probable T2D proxy in NHANES 2021-2023?',fetch_live=False)
  self.assertEqual(b['version'],'V7.7.5')
  self.assertEqual(b['intent'],'POPULATION_ONLY')
 def test_offline_integrated(self):
  q='Investigate finerenone CKD T2D treatment opportunity and NHANES population'
  ext={'pubmed':{'status':'UNAVAILABLE','records':[]},'trials':{'status':'UNAVAILABLE','records':[]}}
  b=build_v774(q,fetch_live=False,external_results=ext,pivotal_results={},abstract_results={'status':'NOT_REQUESTED','records':{}},primary_results={'status':'UNAVAILABLE','records':[],'warnings':['offline']})
  self.assertEqual(b['primary_trial_evidence']['records'],[])
  self.assertIn('No primary publication verified',b['sections'][0]['text'])
if __name__=='__main__':unittest.main()
