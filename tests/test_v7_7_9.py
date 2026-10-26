import unittest
from unittest.mock import patch
import pandas as pd
from src.nhanes_cdc import derive_screening_rows, egfr_2021, load_official_files, compute_official_nhanes, FILES
from src.nhanes_compute import SurveyInputError

class CDCNHANESTests(unittest.TestCase):
    def setUp(self):
        self.data=pd.DataFrame({
            'SEQN':[1,2,3,4,5,6,7,8],
            'RIDAGEYR':[65,65,65,65,65,65,65,17],
            'RIAGENDR':[1,1,1,1,1,1,1,1],
            'SDMVSTRA':[1,1,1,1,2,2,2,2],
            'SDMVPSU':[1,1,2,2,1,1,2,2],
            'LBXSCR':[2.,0.8,2.,0.8,2.,0.8,2.,2.],
            'URDACT':[10.,10.,10.,10.,10.,10.,10.,10.],
            'LBXGH':[7.,7.,5.,5.,7.,7.,5.,7.],
            'DIQ010':[2,2,2,2,2,2,2,2],
            'WTPH2YR':[10.]*8,
        })
    def test_egfr(self):
        self.assertLess(egfr_2021(2,65,1),60)
        self.assertGreater(egfr_2021(.8,65,1),60)
    def test_screening(self):
        d=derive_screening_rows(self.data)
        self.assertEqual(d.screening_flag.tolist()[:7],[1,0,0,0,1,0,0])
        self.assertEqual(d.universe.tolist()[-1],0)
    def test_missing_not_assumed_negative(self):
        d=self.data.copy();d.loc[0,['LBXSCR','URDACT']]=float('nan')
        self.assertTrue(pd.isna(derive_screening_rows(d).screening_flag.iloc[0]))
    def test_unknown_diabetes_subtype_not_claimed(self):
        d=derive_screening_rows(self.data)
        self.assertNotIn('confirmed',str(d.columns))
    def test_offline_mocked_xpt(self):
        from src.nhanes_cdc import COLUMNS
        frames={name:self.data[list(cols)].copy() for name,cols in COLUMNS.items()}
        def fake_read_sas(raw,format):
            name=raw.getvalue().decode('ascii')
            return frames[name]
        with patch('src.nhanes_cdc.pd.read_sas',side_effect=fake_read_sas):
            result=compute_official_nhanes(fetch=lambda url:url.split('/')[-1].split('.')[0].encode('ascii'))
        self.assertEqual(result['estimate'],20)
        self.assertEqual(result['unweighted_positive'],2)
        self.assertEqual(len(result['sources']),len(FILES))
        self.assertIn('not a validation target',result['historical_comparability'])
    def test_bad_file_blocked(self):
        with self.assertRaises(SurveyInputError):load_official_files(fetch=lambda url:b'')

if __name__=='__main__': unittest.main()
