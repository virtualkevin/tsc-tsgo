import unittest
from analyze import classify,PREFIX
class Origins(unittest.TestCase):
 def test_nearest_constructor_once(self):
  r=classify([([2,100,1,50],[PREFIX+'newSymbol',PREFIX+'newSymbolEx',PREFIX+'checkObjectLiteral',PREFIX+'newObjectType'])])
  self.assertEqual(len(r['origins']),1);self.assertEqual(r['origins'][0]['family'],'symbol');self.assertEqual(r['origins'][0]['caller'],'checkObjectLiteral');self.assertEqual(r['selectedSamples']['inuseBytes'],50)
 def test_unselected_and_wrapper_conservation(self):
  r=classify([([1,32,1,32],['runtime.alloc']),([2,64,0,0],[PREFIX+'newObjectType',PREFIX+'newAnonymousType',PREFIX+'instantiateAnonymousType'])])
  self.assertEqual(r['allSamples']['allocBytes'],96);self.assertEqual(r['selectedSamples']['allocBytes'],64);self.assertEqual(r['origins'][0]['caller'],'instantiateAnonymousType')
if __name__=='__main__':unittest.main()
