import copy,unittest
from counts import FIELDS,validate
def fixture():return {'SchemaVersion':1,'Scope':'test','Owners':[{'CheckerID':i+1,'Slots':4096,'SamplingMask':127,'Epoch':0,'Pending':0,'Counts':dict.fromkeys(FIELDS,0)} for i in range(4)]}
class Counts(unittest.TestCase):
 def test_conservation_with_eviction(self):
  d=fixture();c=d['Owners'][0]['Counts'];c.update(Requests=5,Selected=5,FirstInWindow=2,RepeatedCompleted=2,NestedPending=1,Evictions=1,SameObservedState=2,FinishedFirst=1,FinishedRepeated=2,SameResult=1,ChangedResult=1,SameStateAndResult=1,EvictedBeforeFinish=1)
  self.assertEqual(validate(d)['counts']['Requests'],5)
 def test_invalid_count_and_outcome(self):
  for value in [-1,True,1.5]:
   d=fixture();d['Owners'][0]['Counts']['Requests']=value
   with self.assertRaises(AssertionError):validate(d)
  d=fixture();d['Owners'][0]['Counts']['ChangedResult']=1
  with self.assertRaises(AssertionError):validate(d)
 def test_owner_and_pending(self):
  d=fixture();d['Owners'][1]['CheckerID']=1
  with self.assertRaises(AssertionError):validate(d)
  d=fixture();d['Owners'][0]['Pending']=1
  with self.assertRaises(AssertionError):validate(d)
if __name__=='__main__':unittest.main()
