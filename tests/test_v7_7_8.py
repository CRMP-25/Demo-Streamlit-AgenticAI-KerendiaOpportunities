import unittest
import pandas as pd
from src.nhanes_compute import compute_screening_total, SurveyInputError
from src.version import APP_VERSION, download_name


class NHANESComputeTests(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'screen': [1,0,1,0,1,0,1,0],
            'w': [10.0]*8,
            'stratum': [1,1,1,1,2,2,2,2],
            'psu': [1,1,2,2,1,1,2,2],
            'universe': [1,1,1,1,1,1,1,1],
        })
    def run_calc(self, df=None, **kw):
        return compute_screening_total(self.df if df is None else df, flag='screen',weight='w',strata='stratum',psu='psu',**kw)
    def test_weighted_total(self):
        r=self.run_calc()
        self.assertEqual(r['estimate'],40)
        self.assertEqual(r['unweighted_positive'],4)
        self.assertEqual(r['unweighted_known'],8)
        self.assertEqual(r['design_degrees_freedom'],2)
        self.assertIsNotNone(r['ci95_normal_approx'])
    def test_missing_flag_reported(self):
        df=self.df.copy();df.loc[0,'screen']=float('nan')
        r=self.run_calc(df)
        self.assertEqual(r['missing_screening_rows'],1)
        self.assertEqual(r['estimate'],30)
    def test_universe(self):
        df=self.df.copy();df.loc[0,'universe']=0
        r=self.run_calc(df,universe='universe')
        self.assertEqual(r['estimate'],30)
    def test_invalid_binary(self):
        df=self.df.copy();df.loc[0,'screen']=2
        with self.assertRaises(SurveyInputError):self.run_calc(df)
    def test_single_psu_ci_blocked(self):
        df=self.df[self.df.psu==1]
        self.assertIsNone(self.run_calc(df)['ci95_normal_approx'])
    def test_negative_weights_blocked(self):
        df=self.df.copy();df.loc[0,'w']=-1
        with self.assertRaises(SurveyInputError):self.run_calc(df)
    def test_release(self):
        self.assertEqual(APP_VERSION,'V7.7.10')
        self.assertIn('V7_7_10',download_name('Investigation','md'))

if __name__=='__main__': unittest.main()
