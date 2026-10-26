import unittest
import pandas as pd
from src.nhanes_compute import compute_screening_total

class V7710Tests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({'flag':[1,0,None,0,1,0,None,1], 'weight':[10,10,10,10,10,10,10,10], 'strata':[1,1,1,1,2,2,2,2], 'psu':[1,1,2,2,1,1,2,2], 'universe':[1]*8})
    def test_t_interval_and_missing_bounds(self):
        r=compute_screening_total(self.df,flag='flag',weight='weight',strata='strata',psu='psu',universe='universe')
        self.assertEqual(r['estimate'],30)
        self.assertEqual(r['missing_screening_weight'],20)
        self.assertEqual(r['missing_status_sensitivity']['all_missing_positive'],50)
        self.assertGreater(r['ci95_t_critical'],1.96)
        self.assertLessEqual(r['ci95_t_approx'][0],r['ci95_normal_approx'][0])
        self.assertGreaterEqual(r['ci95_t_approx'][1],r['ci95_normal_approx'][1])
    def test_no_missing(self):
        d=self.df.copy();d['flag']=0
        r=compute_screening_total(d,flag='flag',weight='weight',strata='strata',psu='psu')
        self.assertEqual(r['missing_screening_weight'],0)
        self.assertEqual(r['missing_status_sensitivity']['all_missing_positive'],0)
    def test_singleton_suppresses_t_ci(self):
        d=self.df.iloc[:2].copy()
        r=compute_screening_total(d,flag='flag',weight='weight',strata='strata',psu='psu')
        self.assertIsNone(r['ci95_t_approx'])
