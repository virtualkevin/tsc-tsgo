import copy,unittest
from counts import BRANCHES,validate
class Counts(unittest.TestCase):
 def fixture(self):
  row=dict(Branch=13,DeclarationKind=261,CheckMode=0,IncludeOptionality=True,ActiveContext=False,Calls=2,NonNil=1,ErrorResults=0,InclusiveNs=20,ExclusiveNs=10,InclusiveInstantiations=3,ExclusiveInstantiations=1)
  return dict(SchemaVersion=1,Branches=BRANCHES,Owners=[dict(CheckerID=1,Active=False,Rows=[row])])
 def test_reconciles(self):
  result=validate(self.fixture());self.assertEqual(result['calls'],2);self.assertEqual(result['branchCalls'][13],2);self.assertEqual(result['exclusiveNs'],10)
 def test_rejects_incomplete_or_inconsistent(self):
  for mode in ['active','unknown','duplicate','counts','nested']:
   r=self.fixture();owner=r['Owners'][0];row=owner['Rows'][0]
   if mode=='active':owner['Active']=True
   if mode=='unknown':row['Branch']=0
   if mode=='duplicate':owner['Rows'].append(copy.deepcopy(row))
   if mode=='counts':row['NonNil']=3
   if mode=='nested':row['ExclusiveNs']=21
   with self.assertRaises(AssertionError):validate(r)
if __name__=='__main__':unittest.main()
