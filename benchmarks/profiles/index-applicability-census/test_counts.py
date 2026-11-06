import copy,unittest
from counts import validate
class Accounting(unittest.TestCase):
 def fixture(self):
  r=dict(SourceFlags=32,TargetFlags=64,ActiveContext=False,Calls=3,TrackedFirst=1,TrackedRepeat=1,Dropped=1,ChangedResult=1,InclusiveInstantiations=7,ExclusiveInstantiations=5,RepeatExclusiveInstantiations=2,InclusiveRelationGrowth=4,ExclusiveRelationGrowth=3,RepeatExclusiveRelationGrowth=1)
  r["True"]=1
  return dict(SchemaVersion=1,Owners=[dict(CheckerID=1,Active=False,PairLimit=131072,TrackedPairs=1,Rows=[r])])
 def test_counts(self):self.assertEqual(validate(self.fixture())['Calls'],3)
 def test_corrupted_partitions(self):
  for field,value in [('Calls',4),('True',4),('ChangedResult',2),('RepeatExclusiveInstantiations',6)]:
   f=self.fixture();f['Owners'][0]['Rows'][0][field]=value
   with self.assertRaises(AssertionError):validate(f)
 def test_duplicate_owner_or_bucket(self):
  f=self.fixture();f['Owners'].append(copy.deepcopy(f['Owners'][0]))
  with self.assertRaises(AssertionError):validate(f)
  f=self.fixture();f['Owners'][0]['Rows']*=2
  with self.assertRaises(AssertionError):validate(f)
if __name__=='__main__':unittest.main()
