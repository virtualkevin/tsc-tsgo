import unittest
from analyze import analyze, MEMBER, PREFIX

def raw(frames, samples):
    locations='\n'.join(f'{i+1}: 0x{i+1:x} {name} f.go:1:1' for i,name in enumerate(frames))
    return 'Samples:\n'+samples+'\nLocations\n'+locations+'\nMappings\n'

class AuditTests(unittest.TestCase):
    def test_skips_only_named_wrappers(self):
        frames=['runtime.mapaccess1_faststr',MEMBER,PREFIX+'(*Checker).getPropertyOfTypeEx',PREFIX+'(*Checker).getPropertyOfType',PREFIX+'(*Relater).propertiesRelatedTo']
        r=analyze(raw(frames,'  1 10: 1 2 3 4 5'))
        for key in ['memberPath','memberDirectStringMap']:
            self.assertEqual(r[key]['cpuNs'],10)
            self.assertEqual(r[key]['callers'][0]['name'],frames[-1])
    def test_recursive_member_counted_once_at_innermost(self):
        frames=[MEMBER,PREFIX+'(*pendingInstantiatedMembers).get',MEMBER,PREFIX+'outer']
        r=analyze(raw(frames,'  1 10: 1 2 3 4'))
        self.assertEqual(r['memberPath']['cpuNs'],10)
        self.assertEqual(r['memberPath']['callers'][0]['name'],frames[1])
    def test_callee_map_not_attributed_as_direct_member_map(self):
        frames=['runtime.mapaccess1_faststr',PREFIX+'helper',MEMBER,PREFIX+'outer']
        r=analyze(raw(frames,'  1 10: 1 2 3 4'))
        self.assertEqual(r['memberPath']['cpuNs'],10)
        self.assertEqual(r['memberDirectStringMap']['cpuNs'],0)
    def test_generic_map_and_denominator(self):
        frames=['runtime.mapaccess1',MEMBER,PREFIX+'outer','runtime.other']
        r=analyze(raw(frames,'  1 10: 1 2 3\n  2 20: 4'))
        self.assertEqual(r['totalCpuNs'],30)
        self.assertEqual(r['memberDirectStringMap']['cpuNs'],0)
        self.assertAlmostEqual(r['memberPath']['totalPercent'],100/3)
    def test_inlined_member_and_allocation_callee(self):
        text='Samples:\n  1 10: 1 2\nLocations\n1: 0x1 runtime.mallocgc f.go:1:1\n runtime.mapassign_faststr f.go:2:1\n '+MEMBER+' f.go:3:1\n2: 0x2 '+PREFIX+'outer f.go:4:1\nMappings\n'
        r=analyze(text)
        self.assertEqual(r['memberDirectStringMap']['cpuNs'],10)
    def test_inclusive_operation_counted_once_without_member(self):
        frame=PREFIX+'(*Relater).propertiesRelatedTo'
        r=analyze(raw([frame,frame,'runtime.other'],'  1 10: 1 2\n  2 20: 3'))
        self.assertEqual(r['inclusiveOperations']['propertiesRelatedTo']['cpuNs'],10)
        self.assertEqual(r['memberPath']['cpuNs'],0)
    def test_unparsed_location_rejected(self):
        with self.assertRaises(AssertionError):analyze('Samples:\n  1 10: 1\nLocations\n1: 0x1 unknown\nMappings\n')

if __name__=='__main__':unittest.main()
