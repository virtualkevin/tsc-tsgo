import unittest
from counts import validate,CATEGORIES
class CountsTests(unittest.TestCase):
 def fixture(self):return {'SchemaVersion':1,'Categories':CATEGORIES,'Owners':[{'CheckerID':i,'Counts':[0]*33,'Stacks':None} for i in range(1,5)]}
 def test_derived(self):
  d=self.fixture();c=d['Owners'][0]['Counts'];c[0]=20;c[19]=10;c[30]=10;c[1]=10;c[2]=2;c[3]=8;c[4]=11;c[10]=3;c[17]=5;c[11]=4;c[12]=1;c[15]=3
  s=validate(d);self.assertEqual(s['entriesNotMaterializedAtSnapshot'],5);self.assertEqual(s['entryMaterializationFraction'],3/8);self.assertEqual(s['acceptedRelationFraction'],3/4)
 def test_duplicate_owner(self):
  d=self.fixture();d['Owners'][1]['CheckerID']=1
  with self.assertRaises(AssertionError):validate(d)
 def test_impossible_partition(self):
  d=self.fixture();d['Owners'][0]['Counts'][11]=1
  with self.assertRaises(AssertionError):validate(d)
 def test_missing_lookup_classification(self):
  d=self.fixture();d['Owners'][0]['Counts'][0]=1
  with self.assertRaises(AssertionError):validate(d)
 def test_wrong_stack_sample_count(self):
  d=self.fixture();d['Owners'][0]['Counts'][31]=257;d['Owners'][0]['Counts'][32]=771;d['Owners'][0]['Stacks']={'frame':[1,3]}
  with self.assertRaises(AssertionError):validate(d)
if __name__=='__main__':unittest.main()
