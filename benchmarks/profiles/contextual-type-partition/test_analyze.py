import unittest
from analyze import partition,QUERY,PREFIX,source_sites,ROOT

def f(name,line=1):return (QUERY if name=='query' else PREFIX+name,'checker.go',line)

class PartitionTests(unittest.TestCase):
 def test_nearest_recursive_query_owns_sample(self):
  r=partition([(10,[f('work'),f('query',11),f('query',22)])],{'11':'inner','22':'outer'})
  self.assertEqual(r['stageNs'],{'inner':10});self.assertEqual(r['selectedCpuNs'],10)
 def test_outside_and_unknown_are_preserved(self):
  r=partition([(3,[f('work')]),(7,[f('query',99)])],{})
  self.assertEqual(r['totalCpuNs'],10);self.assertEqual(r['stageNs'],{'dispatch_or_unclassified':7});self.assertEqual(r['selectedPercent'],70)
 def test_flat_and_inclusive_have_distinct_meanings(self):
  r=partition([(10,[f('child'),f('work'),f('work'),f('query',1)])],{'1':'a'})
  self.assertEqual(r['flatFunctionsByStage'],{'a':{PREFIX+'child':10}})
  self.assertEqual(r['inclusiveFunctionsByStage'],{'a':{PREFIX+'child':10,PREFIX+'work':10}})
 def test_source_lines_partition_same_helper(self):
  r=partition([(3,[f('work'),f('query',1)]),(7,[f('work'),f('query',2)])],{'1':'a','2':'b'})
  self.assertEqual(r['stageNs'],{'a':3,'b':7});self.assertEqual(sum(r['stagePercentTotal'].values()),100)
 def test_source_sites_are_bound_to_current_query(self):
  sites=source_sites((ROOT/'packages/tsc-go/internal/checker/checker.go').read_text())
  self.assertEqual(len(sites),25);self.assertEqual(sites['29179'],'findContextualNode');self.assertEqual(sites['29232'],'getContextualTypeForJsxAttribute')
  self.assertEqual(list(sites.values()).count('getContextualType'),4)
 def test_negative_samples_rejected(self):
  with self.assertRaises(AssertionError):partition([(-1,[f('query')])],{})

if __name__=='__main__':unittest.main()
