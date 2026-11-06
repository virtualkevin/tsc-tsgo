import copy,unittest
from analyze import analyze
from test_counts import fixture
class AnalyzeTests(unittest.TestCase):
 def test_cohort_merging_and_conservation(self):
  r=fixture();row=copy.deepcopy(r['Owners'][0]['Rows'][0]);row['ContextFlags']=1;r['Owners'][0]['Rows'].append(row);r['Owners'][0]['TrackedRequests']=2
  a=analyze(r);self.assertEqual(len(a['cohorts']),1);self.assertEqual(a['totals']['Calls'],6);self.assertFalse(a['recordedHistoryComplete'])
  self.assertEqual(a['cohorts'][0]['RepeatExclusive'],[2,4,6])
 def test_inference_state_remains_distinct(self):
  r=fixture();row=copy.deepcopy(r['Owners'][0]['Rows'][0]);row['HasInference']=True;row['InferenceSitesBefore']=5;r['Owners'][0]['Rows'].append(row);r['Owners'][0]['TrackedRequests']=2
  a=analyze(r);self.assertEqual(len(a['cohorts']),2);self.assertEqual(a['cohorts'][1]['InferenceSitesBefore'],5)
if __name__=='__main__':unittest.main()
