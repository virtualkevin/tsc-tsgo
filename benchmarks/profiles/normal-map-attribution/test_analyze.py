import unittest
from analyze import analyze
P='github.com/microsoft/typescript-go/internal/checker.'
def raw(samples, locations):
 return 'Samples:\nsamples/count cpu/nanoseconds\n'+samples+'Locations\n'+locations+'Mappings\n'
class AttributionTests(unittest.TestCase):
 def test_nested_maps_assigned_once_to_nearest_project(self):
  r=analyze(raw('  1 100: 1 2 3 4\n',
   '1: 0x1 runtime.mapaccess1 /runtime/map.go:1:1\n'
   '2: 0x2 '+P+'inner /checker.go:1:1\n'
   '3: 0x3 runtime.mapassign /runtime/map.go:2:1\n'
   '4: 0x4 '+P+'outer /checker.go:2:1\n'))
  self.assertEqual(r['mapPathCpuNs'],100)
  self.assertEqual([(x['name'],x['cpuNs']) for x in r['callers']],[(P+'inner',100)])
 def test_inline_generic_and_non_map_sample(self):
  name=P+'Get[go.shape.struct { field int }]'
  r=analyze(raw('  2 200: 1\n  1 100: 2\n',
   '1: 0x1 M=1 internal/runtime/maps.ctrlGroup.matchH2 /maps.go:1:1 s=1(inline)\n'
   '  '+name+' /checker.go:3:2 s=1\n'
   '2: 0x2 '+P+'ordinary /checker.go:4:2\n'))
  self.assertEqual(r['totalCpuNs'],300);self.assertEqual(r['mapPathCpuNs'],200)
  self.assertEqual(r['callers'][0]['name'],name)
 def test_runtime_only_bucket(self):
  r=analyze(raw('  1 10: 1\n','1: 0x1 runtime.mapclear /runtime/map.go:1:1\n'))
  self.assertEqual(r['callers'][0]['name'],'<no project caller>')
 def test_unparsed_sample_location_rejected(self):
  with self.assertRaises(AssertionError):
   analyze(raw('  1 10: 1\n','1: 0x1 broken line\n'))
if __name__=='__main__':unittest.main()
