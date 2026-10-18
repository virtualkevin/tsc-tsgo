import unittest
from analyze import classify,PROJECT
class ClassifyTests(unittest.TestCase):
 def test_nested_frames_count_once(self):
  a=PROJECT+'internal/checker.(*Checker).newType';b=PROJECT+'internal/checker.(*Checker).outer'
  r=classify([([2,128,1,64],[PROJECT+'internal/core.(*Arena[X]).New',a,b]),([3,96,0,0],[a])])
  self.assertEqual(r['total'],dict(allocObjects=5,allocBytes=224,inuseObjects=1,inuseBytes=64))
  self.assertEqual(len(r['owners']),1);self.assertEqual(r['owners'][0]['name'],a)
 def test_runtime_and_zero_samples_conserved(self):
  r=classify([([0,0,0,0],['runtime.mallocgc']),([1,32,1,32],[PROJECT+'internal/collections.foo'])])
  self.assertEqual(len(r['owners']),1);self.assertEqual(r['owners'][0]['inuseBytes'],32)
if __name__=='__main__':unittest.main()
