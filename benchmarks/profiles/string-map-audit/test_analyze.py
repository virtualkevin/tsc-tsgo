import unittest
from analyze import analyze

def raw(frames,samples='  1 10: 1 2 3'):
 return 'Samples:\n'+samples+'\nLocations\n'+frames+'\nMappings\n'

class AuditTests(unittest.TestCase):
 def test_string_map_with_allocation_callee(self):
  r=analyze(raw('1: 0x1 runtime.mallocgc alloc.go:1:1\n2: 0x2 runtime.mapassign_faststr map.go:1:1\n3: 0x3 github.com/microsoft/typescript-go/internal/parser.(*Parser).internIdentifier parser.go:1:1'))
  self.assertEqual(r['fastStringMapPathCpuNs'],10)
  self.assertTrue(r['callers'][0]['name'].endswith('internIdentifier'))
 def test_nested_string_maps_count_once(self):
  r=analyze(raw('1: 0x1 runtime.mapaccess1_faststr m.go:1:1\n2: 0x2 github.com/microsoft/typescript-go/inner i.go:1:1\n3: 0x3 runtime.mapassign_faststr m.go:1:1'))
  self.assertEqual(r['fastStringMapPathCpuNs'],10)
  self.assertEqual(r['callers'][0]['name'],'github.com/microsoft/typescript-go/inner')
 def test_generic_map_is_not_assumed_string(self):
  r=analyze(raw('1: 0x1 runtime.mapaccess1 m.go:1:1\n2: 0x2 github.com/microsoft/typescript-go/inner i.go:1:1\n3: 0x3 runtime.mapassign_fast64 m.go:1:1'))
  self.assertEqual(r['fastStringMapPathCpuNs'],0)
 def test_inline_frames_and_denominator(self):
  r=analyze(raw('1: 0x1 runtime.mapaccess2_faststr m.go:1:1\n github.com/microsoft/typescript-go/helper[go.shape.string] h.go:2:1\n2: 0x2 runtime.other m.go:1:1\n3: 0x3 github.com/microsoft/typescript-go/outer o.go:1:1','  1 10: 1 3\n  2 20: 2 3'))
  self.assertAlmostEqual(r['fastStringMapPathPercent'],100/3)
  self.assertTrue(r['callers'][0]['name'].endswith('[go.shape.string]'))
 def test_unparsed_location_rejected(self):
  with self.assertRaises(AssertionError): analyze(raw('1: 0x1 unknown\n2: 0x2 runtime.mapaccess1_faststr m.go:1:1\n3: 0x3 github.com/microsoft/typescript-go/outer o.go:1:1'))

if __name__=='__main__':unittest.main()
