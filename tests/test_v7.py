import unittest,math
from src.v7 import investigate,population,scenario_analysis,concept_search,_get_json,plan, literature_refresh
from src.release import run_gates
class TestV7(unittest.TestCase):
    def test_all_local_gates(self):self.assertTrue(all(run_gates().values()))
    def test_nhanes_provenance(self):self.assertIn('archive_sha256',population()['provenance'])
    def test_weight_2021(self):self.assertEqual(population()['survey_weight'],'WTPH2YR')
    def test_weight_2015(self):self.assertEqual(population('2015-2016')['survey_weight'],'WTMEC2YR')
    def test_missing_period(self):self.assertEqual(population('2000-2001')['status'],'NO_EVIDENCE')
    def test_eligibility_block(self):self.assertEqual(investigate('How many patients are eligible for Kerendia?')['response']['status'],'BLOCKED_ELIGIBILITY')
    def test_market_block(self):self.assertEqual(investigate('What is the commercial market?')['response']['status'],'BLOCKED_ELIGIBILITY')
    def test_trend_block(self):self.assertEqual(investigate('What is the CKD trend across cycles?')['response']['status'],'BLOCKED_TREND')
    def test_screening_not_diagnosis(self):self.assertIn('screening',investigate('How many adults have CKD and diabetes?')['response']['answer'].lower())
    def test_no_evidence(self):self.assertEqual(investigate('How many Martians?')['response']['status'],'OUT_OF_SCOPE')
    def test_scenario_requires_assumption(self):self.assertEqual(scenario_analysis()['status'],'NEEDS_ASSUMPTION')
    def test_scenario_not_eligibility(self):self.assertEqual(scenario_analysis(fraction=0.2)['status'],'HYPOTHETICAL_ARITHMETIC_ONLY')
    def test_invalid_scenario(self):
        for value in [-0.1,1.1,float('nan'),True]:
            with self.subTest(value=value),self.assertRaises(ValueError):scenario_analysis(fraction=value)
    def test_concept_retrieval_not_validated(self):
        for n in concept_search('chronic kidney disease'):self.assertEqual(n['mapping_status'],'NOT_CLINICALLY_VALIDATED')
    def test_external_off_by_default(self):self.assertEqual(investigate('latest PubMed literature')['tools']['external_literature_live']['status'],'NOT_REQUESTED_FOR_EXECUTION')
    def test_disallow_untrusted_hosts(self):
        with self.assertRaises(ValueError):_get_json('https://github.com/anything')
    def test_reject_long_input(self):
        with self.assertRaises(ValueError):investigate('a'*1501)
    def test_plan_is_bounded(self):self.assertLessEqual(len(plan('finerenone literature and CKD population')),4)
if __name__=='__main__':unittest.main()
