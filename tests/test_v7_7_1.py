import unittest, io, urllib.error
from unittest.mock import patch
from src import v77

class V771ReliabilityTests(unittest.TestCase):
 def test_retry_429_then_success(self):
  class Response:
   status=200
   def __enter__(self):return self
   def __exit__(self,*args):return False
   def read(self,n):return b'actual-source-bytes'
  error=urllib.error.HTTPError('https://eutils.ncbi.nlm.nih.gov/',429,'rate limit',{},io.BytesIO())
  with patch('src.v77.urllib.request.urlopen',side_effect=[error,Response()]) as call:
   with patch('src.v77.time.sleep') as sleep:
    self.assertEqual(v77._request_bytes('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'),'actual-source-bytes'.encode())
    self.assertEqual(call.call_count,2);sleep.assert_called_once()
 def test_non_retryable_403(self):
  err=urllib.error.HTTPError('https://eutils.ncbi.nlm.nih.gov/',403,'forbidden',{},io.BytesIO())
  with patch('src.v77.urllib.request.urlopen',side_effect=err) as call:
   with self.assertRaises(v77.EvidenceUnavailable):v77._request_bytes('https://eutils.ncbi.nlm.nih.gov/a')
   self.assertEqual(call.call_count,1)
 def test_disallowed_hosts(self):
  with self.assertRaises(v77.EvidenceUnavailable):v77._request_bytes('https://evil.example/a')
 def test_cache_reuses_only_real_retrieved_response(self):
  v77._CACHE.clear();calls=[]
  def producer():calls.append(1);return {'status':'RETRIEVED','records':[{'pmid':'TEST_SOFTWARE_ONLY'}]}
  v77._cached('software-test',producer);v77._cached('software-test',producer)
  self.assertEqual(len(calls),1);v77._CACHE.clear()
 def test_failure_not_cached(self):
  v77._CACHE.clear();calls=[]
  def producer():calls.append(1);return {'status':'UNAVAILABLE','records':[]}
  v77._cached('software-test',producer);v77._cached('software-test',producer)
  self.assertEqual(len(calls),2)
 def test_original_graph_only(self):
  from src.engine import integrity
  self.assertEqual(integrity()['baseline_sha256'],'4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf')
if __name__=='__main__':unittest.main()
