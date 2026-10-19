import copy,json,unittest
from analyze import summarize
from counts import KINDS
class Origins(unittest.TestCase):
 def fixture(self,unresolved=False):
  key=json.dumps({'Kind':5,'Unresolved':unresolved,'Name':'p'})
  record=dict(Kind=5,Calls=1,Completed=1,Cached=1,ErrorResults=0,InclusiveNs=10,ExclusiveNs=8,InclusiveInstantiations=3,ExclusiveInstantiations=2)
  owner=dict(CheckerID=1,Active=False,Hits=[0]*9,Misses=[0,0,0,0,0,1,0,0,0],Origins={key:record},DroppedOrigins=0)
  other=copy.deepcopy(owner);other['CheckerID']=2
  return dict(SchemaVersion=1,Kinds=KINDS,Owners=[owner,other])
 def test_same_full_origin_across_owners(self):
  r=summarize(self.fixture())['kinds'][5]
  self.assertEqual((r['repeatedOriginDescriptors'],r['repeatedOriginCalls'],r['repeatedOriginExclusiveNs']),(1,2,16))
 def test_unresolved_excluded(self):
  r=summarize(self.fixture(True))['kinds'][5]
  self.assertEqual(r['repeatedOriginCalls'],0);self.assertEqual(r['unresolvedCalls'],2)
 def test_distinct_descriptors_not_collapsed(self):
  r=self.fixture();owner=r['Owners'][1];key=next(iter(owner['Origins']));value=owner['Origins'].pop(key);d=json.loads(key);d['Name']='q';owner['Origins'][json.dumps(d)]=value
  self.assertEqual(summarize(r)['kinds'][5]['repeatedOriginDescriptors'],0)
if __name__=='__main__':unittest.main()
