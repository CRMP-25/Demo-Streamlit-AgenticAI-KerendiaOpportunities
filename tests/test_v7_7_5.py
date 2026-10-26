import unittest
from unittest.mock import patch
from src.v775 import PRIMARY_CANDIDATES, retrieve_primary_papers, effect_table, kg_assertion_review, build_v775
from src.version import APP_VERSION, download_name

class TestV775(unittest.TestCase):
    def test_version(self):
        self.assertEqual(APP_VERSION, 'V7.7.6')
        self.assertEqual(download_name('Investigation','md'),'Healthcare_Intelligence_Investigation_V7_7_6.md')
    def test_figaro_correct_title(self):
        self.assertEqual(PRIMARY_CANDIDATES['FIGARO-DKD'],
            ('34449181','Cardiovascular Events with Finerenone in Kidney Disease and Type 2 Diabetes'))
    def test_verify_figaro(self):
        import json
        from src.v775 import verify_primary_candidate
        good={'result':{'34449181':{'title':'Cardiovascular Events with Finerenone in Kidney Disease and Type 2 Diabetes.'},
                        '33264825':{'title':'Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes.'}}}
        with patch('src.v775._request_bytes',return_value=json.dumps(good).encode()):
            result=retrieve_primary_papers()
        self.assertEqual(len(result['records']),2)
    def test_no_abstract_no_effects(self):
        self.assertIn('No source-verified',effect_table([{'study':'FIGARO-DKD','pmid':'34449181',
            'verification':'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL','abstract_sections':[]}]))
    def test_figaro_descriptive_difference(self):
        text=effect_table([{'study':'FIGARO-DKD','pmid':'34449181',
            'verification':'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL',
            'abstract_sections':[{'label':'Results','text':'A primary outcome occurred in 12.4% and 14.2% of participants, respectively.'}]}])
        self.assertIn('-1.8 percentage points',text)
        self.assertNotIn('9.5%',text)
    def test_kg_flag(self):
        warning=kg_assertion_review({'graph_edges':[{'source':'DR6','target':'D1','relation':'treats'}]})
        self.assertIn('REVIEW REQUIRED',warning)
    def test_population_no_network(self):
        b=build_v775('How many US adults meet the CKD screening and probable T2D proxy in NHANES 2021-2023?',fetch_live=False)
        self.assertEqual(b['intent'],'POPULATION_ONLY')
        self.assertEqual(b['version'],'V7.7.6')
    def test_integrated_offline(self):
        q='Investigate finerenone CKD T2D treatment opportunity and NHANES population'
        b=build_v775(q,fetch_live=False,external_results={'pubmed':{'status':'UNAVAILABLE','records':[]},'trials':{'status':'UNAVAILABLE','records':[]}},pivotal_results={},abstract_results={'status':'NOT_REQUESTED','records':{}},primary_results={'status':'UNAVAILABLE','records':[],'warnings':['offline']})
        self.assertTrue(any(s['title'].startswith('Primary trial event-rate comparison') for s in b['sections']))
        self.assertTrue(any(s['title']=='Preserved KG assertion quality review' for s in b['sections']))

if __name__=='__main__': unittest.main()
