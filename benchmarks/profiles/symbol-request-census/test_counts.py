import unittest,copy
from counts import validate,FIELDS,KINDS
def fixture():
 return {'SchemaVersion':1,'MapperKinds':KINDS,'Owners':[{'CheckerID':i+1,'Limit':32768,'TrackedKeys':0,'Counts':[{k:0 for k in FIELDS} for _ in KINDS]} for i in range(4)]}
class Counts(unittest.TestCase):
 def test_conservation_and_mutation(self):
  d=fixture();o=d['Owners'][0];o['TrackedKeys']=1;o['Counts'][1].update(Requests=4,NewKeys=1,RepeatedSameObservedState=2,RepeatedChangedObservedState=1)
  self.assertEqual(validate(d)['totals']['Requests'],4)
  broken=copy.deepcopy(d);broken['Owners'][0]['Counts'][1]['Requests']=3
  with self.assertRaises(AssertionError):validate(broken)
 def test_unknown_requires_full_capacity(self):
  d=fixture();d['Owners'][0]['Counts'][0].update(Requests=1,UntrackedAtCapacity=1)
  with self.assertRaises(AssertionError):validate(d)
 def test_duplicate_owner_rejected(self):
  d=fixture();d['Owners'][1]['CheckerID']=1
  with self.assertRaises(AssertionError):validate(d)
if __name__=='__main__':unittest.main()
