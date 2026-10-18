import unittest
from unittest.mock import patch
import analyze

class Attribution(unittest.TestCase):
    def test_exact_typed_helpers(self):
        self.assertTrue(analyze.direct_type_list('slices.Clone[go.shape.[]*'+analyze.TYPE+',go.shape.*uint8]'))
        self.assertTrue(analyze.direct_type_list('github.com/microsoft/typescript-go/internal/checker.instantiateList[go.shape.*'+analyze.TYPE+']'))
    def test_ambiguous_and_struct_shapes_excluded(self):
        self.assertFalse(analyze.direct_type_list('slices.Clone[go.shape.[]go.shape.*uint8,go.shape.*uint8]'))
        self.assertFalse(analyze.direct_type_list('slices.Grow[go.shape.[]go.shape.struct { value *'+analyze.TYPE+' },go.shape.struct {}]'))
    def test_child_allocations_not_attributed_to_outer_list(self):
        builder='github.com/microsoft/typescript-go/internal/checker.instantiateList[go.shape.*'+analyze.TYPE+']'
        samples=[([3,40,2,30],['checker.newObjectType',builder]),([2,20,1,10],[builder])]
        with patch.object(analyze.parser,'parse',return_value=iter(samples)):r=analyze.analyze('unused')
        self.assertEqual(r['total']['allocBytes'],60)
        self.assertEqual(r['selectedDirectSites']['allocBytes'],20)
        self.assertEqual(len(r['sites']),1)
    def test_multiple_matching_frames_count_once(self):
        frame='slices.Insert[go.shape.[]*'+analyze.TYPE+',go.shape.*uint8]'
        with patch.object(analyze.parser,'parse',return_value=iter([([1,8,1,8],[frame,frame])])):r=analyze.analyze('unused')
        self.assertEqual(r['selectedDirectSites']['allocBytes'],8)

if __name__=='__main__':unittest.main()
