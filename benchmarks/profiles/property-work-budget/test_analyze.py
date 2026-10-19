import unittest
from analyze import analyze
class Attribution(unittest.TestCase):
 def test_overlapping_categories_count_once(self):
  raw='Samples:\n  1 20: 1 2\n  1 30: 2\n  1 50: 3\nLocations\n  1: 0x1 github.com/microsoft/typescript-go/internal/checker.(*Relater).propertiesRelatedTo x.go:1:1\n  2: 0x2 github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateSymbol x.go:2:1\n  3: 0x3 runtime.other x.go:3:1\nMappings\n'
  r=analyze(raw);self.assertEqual(r['totalCpuNs'],100);self.assertEqual(r['propertyUnionPercent'],50);self.assertEqual(r['inclusivePercent']['property_relation'],20);self.assertEqual(r['inclusivePercent']['member_materialization'],50);self.assertEqual(sum(r['exclusiveBucketsNs'].values()),100)
 def test_unparsed_frame_fails(self):
  with self.assertRaises(AssertionError):analyze('Samples:\n  1 20: 1\nLocations\n  1: 0x1 undecodable\nMappings\n')
if __name__=='__main__':unittest.main()
