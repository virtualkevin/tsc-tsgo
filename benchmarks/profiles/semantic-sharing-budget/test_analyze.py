import importlib.util,unittest
from analyze import PARSER,PATTERNS
spec=importlib.util.spec_from_file_location('partition',PARSER)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.PATTERNS=PATTERNS
class Attribution(unittest.TestCase):
 def test_recursive_and_overlapping_samples(self):
  raw='Samples:\n  1 20: 1 1 2\n  1 30: 2\n  1 50: 3\nLocations\n  1: 0x1 github.com/microsoft/typescript-go/internal/checker.(*Checker).getSignatureFromDeclaration x.go:1:1\n  2: 0x2 github.com/microsoft/typescript-go/internal/checker.(*Checker).getReturnTypeOfSignature x.go:2:1\n  3: 0x3 runtime.other x.go:3:1\nMappings\n'
  r=m.analyze(raw)
  self.assertEqual(r['totalCpuNs'],100)
  self.assertEqual(r['inclusivePercent']['signature_construction'],20)
  self.assertEqual(r['inclusivePercent']['return_type_resolution'],50)
  self.assertEqual(r['exclusiveBucketsNs'],{'signature_construction+return_type_resolution':20,'return_type_resolution':30,'outside':50})
 def test_unknown_frame_is_not_silently_dropped(self):
  with self.assertRaises(AssertionError):m.analyze('Samples:\n  1 20: 1\nLocations\n  1: 0x1 invalid\nMappings\n')
if __name__=='__main__':unittest.main()
