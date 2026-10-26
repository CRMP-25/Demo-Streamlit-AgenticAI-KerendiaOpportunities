import unittest
from pathlib import Path
from src.version import FILE_VERSION, download_name
from src.v773 import APP_VERSION
from src.v773 import build_v773, to_markdown, classify_study, complete_source_sections

class TestV773(unittest.TestCase):
    def test_filename_version(self):
        self.assertEqual(download_name('Investigation','md'),'Healthcare_Intelligence_Investigation_V7_7_9.md')
        self.assertEqual(download_name('Report','md'),'Healthcare_Intelligence_Report_V7_7_9.md')
        self.assertEqual(download_name('Evidence','json'),'Healthcare_Intelligence_Evidence_V7_7_9.json')
        self.assertEqual('V7_7_9',FILE_VERSION)
    def test_app_downloads_not_hardcoded(self):
        app=(Path(__file__).parents[1]/'app.py').read_text()
        self.assertIn("download_name('Investigation','md')",app)
        self.assertNotIn('Healthcare_Intelligence_Investigation_V7_7_1.md',app)
    def test_study_type_not_guaranteed(self):
        self.assertIn('HEURISTIC',classify_study('Kidney outcomes: an analysis from FIGARO-DKD','FIGARO-DKD'))
    def test_full_source_section(self):
        full='A full source sentence. A second sentence with a conclusion.'
        self.assertEqual(complete_source_sections({'abstract_available':True,'sections':[{'label':'Results','text':full}]})[0]['text'],full)
    def test_population_no_external(self):
        b=build_v773('How many US adults meet the CKD screening and probable T2D proxy in NHANES 2021-2023?',fetch_live=False)
        self.assertEqual(b['intent'],'POPULATION_ONLY')
        self.assertEqual(b['version'],APP_VERSION)
        self.assertEqual(b['external']['pubmed']['status'],'NOT_REQUESTED')
        self.assertIn('V7.7.3',to_markdown(b).splitlines()[0])
    def test_integrated_no_fabrication(self):
        external={'pubmed':{'status':'UNAVAILABLE','records':[]},'trials':{'status':'UNAVAILABLE','records':[]}}
        b=build_v773('Investigate the clinical evidence, population characteristics, and potential treatment opportunity for finerenone in CKD and T2D',fetch_live=False,external_results=external,pivotal_results={},abstract_results={'status':'NOT_REQUESTED','records':{}})
        self.assertEqual(b['version'],APP_VERSION)
        self.assertIn('Executive evidence synthesis and decision gaps', [x['title'] for x in b['sections']])
        self.assertEqual(b['structured_evidence'],[])
        self.assertIn('V7.7.3',to_markdown(b).splitlines()[0])

if __name__=='__main__':unittest.main()
