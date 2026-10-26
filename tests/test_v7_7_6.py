import unittest
from src.v776 import build_v776, integrated_synthesis, consolidated_pivotal_table, to_markdown
from src.version import APP_VERSION, download_name

class TestV776(unittest.TestCase):
    def test_version(self):
        self.assertEqual(APP_VERSION,'V7.7.10')
        self.assertIn('V7_7_10',download_name('Investigation','md'))
    def test_no_unsourced_primary_numbers(self):
        s,_=integrated_synthesis({'primary_trial_evidence':{'records':[]}})
        self.assertNotIn('17.8%',s)
        self.assertIn('blocked',s.lower())
    def test_verified_source_pairs(self):
        r=[{'study':'FIDELIO-DKD','pmid':'33264825','verification':'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL','abstract_sections':[{'label':'RESULTS','text':'17.8% and 21.1%'}]},
           {'study':'FIGARO-DKD','pmid':'34449181','verification':'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL','abstract_sections':[{'label':'RESULTS','text':'12.4% and 14.2%'}]}]
        s,refs=integrated_synthesis({'primary_trial_evidence':{'records':r}})
        self.assertIn('17.8%',s)
        self.assertIn('12.4%',s)
        self.assertEqual(refs,['33264825','34449181'])
    def test_primary_first_in_register(self):
        s=consolidated_pivotal_table({'primary_trial_evidence':{'records':[{'study':'FIGARO-DKD','pmid':'34449181','abstract_sections':[]}]},'structured_evidence':[{'study':'FIDELITY','pmid':'35023547'}]})
        self.assertLess(s.index('34449181'),s.index('35023547'))
    def test_integrated_offline(self):
        b=build_v776('Investigate finerenone CKD T2D treatment opportunity and NHANES population',fetch_live=False)
        self.assertEqual(b['version'],'V7.7.10')
        self.assertTrue(any(s['title'].startswith('Integrated clinical intelligence synthesis') for s in b['sections']))
        self.assertIn('V7.7.10',to_markdown(b).splitlines()[0])
    def test_population_fast_path(self):
        b=build_v776('How many US adults meet the CKD screening and probable T2D proxy in NHANES 2021-2023?',fetch_live=False)
        self.assertEqual(b['intent'],'POPULATION_ONLY')
        self.assertFalse(any(s['title'].startswith('Integrated clinical intelligence synthesis') for s in b['sections']))

if __name__=='__main__':unittest.main()
