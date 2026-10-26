import unittest
from src.v777 import evidence_gap_analysis, build_v777, to_markdown
from src.version import APP_VERSION

class TestV777(unittest.TestCase):
    def test_release(self):
        self.assertEqual(APP_VERSION,'V7.7.10')
    def test_no_fake_efficacy(self):
        a=evidence_gap_analysis({'primary_trial_evidence':{'records':[]},'sections':[]})
        self.assertFalse(any(a['verified_primary'].values()))
        self.assertEqual(a['eligible_population_status'],'BLOCKED')
        self.assertFalse(a['new_nhanes_analysis_performed'])
    def test_verified_source_requires_matching_identity_and_abstract(self):
        r={'study':'FIDELIO-DKD','pmid':'33264825','verification':'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL',
           'abstract_sections':[{'label':'RESULTS','text':'17.8% versus 21.1%'}]}
        a=evidence_gap_analysis({'primary_trial_evidence':{'records':[r]},'sections':[]})
        self.assertTrue(a['verified_primary']['FIDELIO-DKD'])
        r['pmid']='00000000'
        self.assertFalse(evidence_gap_analysis({'primary_trial_evidence':{'records':[r]},'sections':[]})['verified_primary']['FIDELIO-DKD'])
    def test_offline_integration(self):
        b=build_v777('Investigate finerenone CKD T2D treatment opportunity and NHANES population',fetch_live=False)
        self.assertEqual(b['version'],'V7.7.10')
        self.assertIn('evidence_gap_analysis',b)
        self.assertIn('not estimable',b['sections'][0]['text'].lower())
        self.assertIn('V7.7.10',to_markdown(b).splitlines()[0])
    def test_population_fast_path(self):
        b=build_v777('How many US adults meet the CKD screening and probable T2D proxy in NHANES 2021-2023?',fetch_live=False)
        self.assertEqual(b['intent'],'POPULATION_ONLY')
        self.assertNotIn('evidence_gap_analysis',b)

if __name__=='__main__': unittest.main()
