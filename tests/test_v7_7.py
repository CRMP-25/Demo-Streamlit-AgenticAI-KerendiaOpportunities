import unittest
from unittest.mock import patch
from src.v77 import build_v77, graph_connections, fetch_abstracts, to_markdown
from src.engine import integrity

Q='Investigate clinical evidence, population opportunity for finerenone Kerendia CKD and type 2 diabetes'
EMPTY={'pubmed':{'status':'UNAVAILABLE','records':[],'error':'test offline'},'trials':{'status':'UNAVAILABLE','records':[],'error':'test offline'}}
class TestV77(unittest.TestCase):
 def test_integrity(self):self.assertEqual(integrity()['baseline_sha256'],'4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf')
 def test_no_fabricated_evidence(self):
  r=build_v77(Q,fetch_live=False,external_results=EMPTY)
  self.assertEqual(r['version'],'V7.7');self.assertFalse(r['pivotal_evidence']);self.assertEqual(r['abstract_evidence']['status'],'NOT_REQUESTED')
  self.assertIn('No percentage or market number inferred',to_markdown(r))
 def test_original_edges_only(self):
  r=build_v77(Q,fetch_live=False,external_results=EMPTY)
  self.assertTrue(all('source' in x and 'relation' in x and 'target' in x for x in r['graph_edges']))
 def test_abstract_excerpt_attributed(self):
  pivotal={'FIDELIO-DKD':{'status':'RETRIEVED','records':[{'pmid':'12345','title':'TEST SOFTWARE FIXTURE','url':'https://pubmed.ncbi.nlm.nih.gov/12345/'}]}}
  abstract={'status':'RETRIEVED','records':{'12345':{'sections':[{'label':'RESULTS','text':'TEST FIXTURE TEXT ONLY'}]}}}
  r=build_v77(Q,fetch_live=False,external_results=EMPTY,pivotal_results=pivotal,abstract_results=abstract)
  self.assertIn('TEST FIXTURE TEXT ONLY',to_markdown(r));self.assertIn('not critically appraised',to_markdown(r))
 def test_absent_abstract_does_not_invent(self):
  pivotal={'FIGARO-DKD':{'status':'RETRIEVED','records':[{'pmid':'54321','title':'TEST ONLY','url':'https://pubmed.ncbi.nlm.nih.gov/54321/'}]}}
  r=build_v77(Q,fetch_live=False,external_results=EMPTY,pivotal_results=pivotal,abstract_results={'status':'UNAVAILABLE','records':{}})
  self.assertIn('Study outcomes not extracted',to_markdown(r))
 def test_no_ids_no_http(self):self.assertEqual(fetch_abstracts(['not-a-pmid'])['status'],'NO_EVIDENCE')
if __name__=='__main__':unittest.main()
