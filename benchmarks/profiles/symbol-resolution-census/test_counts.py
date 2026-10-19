import copy,json,unittest
from counts import validate,KINDS
class Counts(unittest.TestCase):
 def fixture(self):
  record=dict(Kind=5,Calls=2,Completed=2,Cached=1,ErrorResults=0,InclusiveNs=10,ExclusiveNs=6,InclusiveInstantiations=3,ExclusiveInstantiations=2)
  return {'SchemaVersion':1,'Kinds':KINDS,'Owners':[{'CheckerID':1,'Active':False,'Hits':[0]*9,'Misses':[0,0,0,0,0,2,0,0,0],'Origins':{json.dumps({'Kind':5,'Unresolved':True}):record},'DroppedOrigins':0}]}
 def test_totals(self):
  self.assertEqual(validate(self.fixture()),dict(hits=0,misses=2,recorded=2,dropped=0,unresolvedCalls=2,owners=1))
 def test_active_or_inconsistent_counts_rejected(self):
  for mode in ['active','miss','exclusive','duplicate']:
   r=self.fixture();o=r['Owners'][0]
   if mode=='active':o['Active']=True
   if mode=='miss':o['Misses'][5]=3
   if mode=='exclusive':next(iter(o['Origins'].values()))['ExclusiveNs']=11
   if mode=='duplicate':r['Owners'].append(copy.deepcopy(o))
   with self.assertRaises(AssertionError):validate(r)
if __name__=='__main__':unittest.main()
