import copy,unittest
from counts import validate,SCALARS,ARRAYS

def fixture():
 row={k:0 for k in SCALARS};row.update({k:[0,0,0] for k in ARRAYS});row.update(Kind=1,TypeFlags=0,ObjectFlags=0,ActiveContext=False,Calls=3,NonNil=2,TrackedFirst=1,TrackedRepeat=1,Dropped=1,ChangedResult=1,Inclusive=[4,6,8],Exclusive=[3,5,7],RepeatExclusive=[1,2,3],InclusiveNs=5,ExclusiveNs=4,ExclusiveRelationGrowth=-1)
 return {'SchemaVersion':1,'Owners':[{'CheckerID':1,'Active':False,'RequestLimit':131072,'TrackedRequests':1,'Rows':[row]}]}
class CountsTests(unittest.TestCase):
 def test_conservation_and_empty_workload(self):
  self.assertEqual(validate(fixture())['Calls'],3)
  r=fixture();r['Owners'][0].update(Rows=[],TrackedRequests=0);self.assertEqual(validate(r)['Calls'],0)
 def test_reject_bad_partition_and_context(self):
  for key,value in [('Calls',4),('Exclusive',[9,5,7]),('Kind',3),('ChangedResult',2)]:
   r=fixture();r['Owners'][0]['Rows'][0][key]=value
   with self.assertRaises(AssertionError):validate(r)
 def test_reject_duplicate_owner_and_request_mismatch(self):
  r=fixture();r['Owners'].append(copy.deepcopy(r['Owners'][0]))
  with self.assertRaises(AssertionError):validate(r)
  r=fixture();r['Owners'][0]['TrackedRequests']=2
  with self.assertRaises(AssertionError):validate(r)
if __name__=='__main__':unittest.main()
