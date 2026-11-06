import unittest
from analyze import partition,decode,PREFIX

def f(name,line=1):return (PREFIX+name,'checker.go',line)
class PartitionTests(unittest.TestCase):
 def test_nested_call_has_one_owner(self):
  r=partition([(10,[f('work'),f('resolveCall',22),f('inferTypeArguments'),f('chooseOverload'),f('resolveCall',20)]),(5,[f('elsewhere')])],{20:'subtype',22:'assignable'})
  self.assertEqual(r['callCpuNs'],10);self.assertEqual(r['phaseNs'],{'call_body_other':10});self.assertEqual(r['chooseOverloadCpuNs'],0);self.assertEqual(r['totalCpuNs'],15)
 def test_nearest_phase_and_recursive_dedup(self):
  r=partition([(7,[f('getSignatureInstantiation'),f('inferTypeArguments'),f('inferTypeArguments'),f('chooseOverload'),f('resolveCall',20)])],{20:'subtype'})
  self.assertEqual(r['phaseSourceLineNs'],{'getSignatureInstantiation:1':7});self.assertEqual(r['phaseNs'],{'signature_instantiation':7});self.assertEqual(r['passNs'],{'subtype':7})
 def test_unknown_boundary_is_retained(self):
  r=partition([(3,[f('chooseOverload'),f('resolveCall',99)]),(4,[f('chooseOverload'),f('resolveNewExpression')])],{20:'subtype'})
  self.assertEqual(r['passNs'],{'unclassified_choose_boundary':4,'unclassified_choose_site':3})
 def test_inline_frame_order(self):
  raw='Samples:\n  1 10: 1 2\nLocations\n 1: 0xab M=1 '+PREFIX+'isSignatureApplicable checker.go:12:0 s=10\n '+PREFIX+'chooseOverload checker.go:15:0 s=10\n 2: 0xcd M=1 '+PREFIX+'resolveCall checker.go:20:0 s=1\nMappings\n'
  r=partition(decode(raw),{20:'subtype'});self.assertEqual(r['phaseByPassNs'],{'applicability / subtype':10})
 def test_unparsed_location_rejected(self):
  with self.assertRaises(AssertionError):list(decode('Samples:\n  1 10: 1\nLocations\n 1: 0xab M=1 bad\nMappings\n'))
if __name__=='__main__':unittest.main()
