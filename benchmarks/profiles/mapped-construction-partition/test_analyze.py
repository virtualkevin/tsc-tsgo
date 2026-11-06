import unittest
from analyze import METHOD,partition,sites_from_source,ROOT,owns

def f(name,line=1):return (name,'checker.go',line)
class OwnershipTests(unittest.TestCase):
 def test_closest_closure_owns(self):
  r=partition([(10,[f('work'),f(METHOD+'.func2.1',2),f(METHOD,1)])],{'1':'outer','2':'inner'})
  self.assertEqual(r['stageNs'],{'inner':10});self.assertEqual(r['ownerFramesNs'],{METHOD+'.func2.1':10})
 def test_recursive_construction_not_counted_twice(self):
  r=partition([(10,[f(METHOD,2),f(METHOD+'.func1',1),f(METHOD,3)])],{'2':'publication','1':'modifier_property'})
  self.assertEqual(r['selectedCpuNs'],10);self.assertEqual(r['stageNs'],{'publication':10})
 def test_inclusive_recursion_and_flat_are_separate(self):
  r=partition([(5,[f('child'),f('helper'),f('helper'),f(METHOD,1)])],{'1':'modifier_index'})
  self.assertEqual(r['inclusiveFunctionsByStage'],{'modifier_index':{'child':5,'helper':5}});self.assertEqual(r['flatFunctionsByStage'],{'modifier_index':{'child':5}})
 def test_unknown_and_outside_samples_conserved(self):
  r=partition([(3,[f('work')]),(7,[f(METHOD,99)])],{})
  self.assertEqual(r['totalCpuNs'],10);self.assertEqual(r['stageNs'],{'dispatch_or_unclassified':7});self.assertEqual(r['selectedPercent'],70)
 def test_similar_unrelated_name_excluded(self):
  self.assertFalse(owns(METHOD+'Other'));self.assertTrue(owns(METHOD+'.func1'))
 def test_pinned_source_classifies_semantic_operations(self):
  s=sites_from_source((ROOT/'packages/tsc-go/internal/checker/checker.go').read_text())
  self.assertEqual(list(s.values()).count('publication'),2);self.assertEqual(list(s.values()).count('link_tables'),4);self.assertEqual(list(s.values()).count('modifier_index'),1)
if __name__=='__main__':unittest.main()
