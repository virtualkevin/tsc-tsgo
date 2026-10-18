import unittest
from analyze import analyze,ARENA,AST,PROJECT

def raw(frames, samples=' 2 200 1 100: 1 2 3\n'):
 return 'Samples:\nalloc_objects/count alloc_space/bytes[dflt] inuse_objects/count inuse_space/bytes\n'+samples+'Locations\n'+''.join(f'{i}: 0x123 M=1 {f} file.go:1:0 s=1\n' for i,f in enumerate(frames,1))+'Mappings\n'
class AuditTests(unittest.TestCase):
 def test_ast_arena_owner(self):
  r=analyze(raw(['slices.Grow[[]T]',ARENA+'T]).New',AST+'(*NodeFactory).NewIdentifier']))
  self.assertEqual(r['astOwnedArena']['allocBytes'],200)
  self.assertEqual(r['arena']['allocObjects'],2)
 def test_non_arena_excluded(self):
  r=analyze(raw(['runtime.mallocgc','slices.Grow[[]T]',AST+'(*NodeFactory).NewIdentifier']))
  self.assertEqual(r['total']['allocBytes'],200);self.assertEqual(r['arena']['allocBytes'],0)
 def test_non_ast_owner(self):
  r=analyze(raw([ARENA+'T]).New',PROJECT+'internal/checker.(*Checker).newSymbol',AST+'outer']))
  self.assertEqual(r['arena']['allocBytes'],200);self.assertEqual(r['astOwnedArena']['allocBytes'],0)
 def test_wrappers_and_inline_frames(self):
  text=raw([ARENA+'T]).NewSlice',ARENA+'T]).Clone',AST+'(*NodeFactory).NewNodeList'])
  text=text.replace('2: 0x123 M=1 ','  ')
  text=text.replace(': 1 2 3',': 1 3')
  r=analyze(text);self.assertEqual(r['owners'][0]['name'],AST+'(*NodeFactory).NewNodeList')
 def test_samples_summed_once(self):
  r=analyze(raw([ARENA+'T]).New',AST+'inner',ARENA+'T]).New'],' 2 200 1 100: 1 2 3\n 3 300 2 200: 1 2 3\n'))
  self.assertEqual(r['arena']['allocBytes'],500);self.assertEqual(r['total']['inuseBytes'],300)
 def test_missing_location_rejected(self):
  with self.assertRaises(AssertionError):analyze(raw(['x'],' 1 1 1 1: 2\n'))
if __name__=='__main__':unittest.main()
