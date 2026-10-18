import unittest,copy
from counts import validate,CATEGORIES
def fixture():return {'SchemaVersion':1,'Categories':CATEGORIES,'Owners':[{'CheckerID':i+1,'Counts':[0]*8} for i in range(4)]}
class Counts(unittest.TestCase):
 def test_totals(self):
  d=fixture();d['Owners'][0]['Counts']=[1,2,3,4,5,6,7,8];r=validate(d);self.assertEqual(r['constructorRequests'],36);self.assertEqual(r['syntacticCandidates'],8)
 def test_invalid_counts(self):
  for value in [-1,1.5,True]:
   d=fixture();d['Owners'][0]['Counts'][0]=value
   with self.assertRaises(AssertionError):validate(d)
 def test_duplicate_owner_and_category_order(self):
  d=fixture();d['Owners'][1]['CheckerID']=1
  with self.assertRaises(AssertionError):validate(d)
  d=fixture();d['Categories']=list(reversed(CATEGORIES))
  with self.assertRaises(AssertionError):validate(d)
if __name__=='__main__':unittest.main()
