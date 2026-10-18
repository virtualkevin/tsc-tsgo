import unittest
from counts import FIELDS,FAMILY_FIELDS,validate
TYPES=['parameter','reference','reverse-mapped','object-instantiation','other-object','union','intersection','index','indexed-access','template','string-mapping','conditional','substitution','other','reserved14','reserved15']
MAPPERS=['nil','simple','array','array-single','deferred','function','merged','composite','inference','other']
def fixture():
 return {'SchemaVersion':2,'Scope':'test','TypeFamilies':TYPES[:],'MapperFamilies':MAPPERS[:],'Owners':[{'CheckerID':i+1,'Slots':4096,'SamplingMask':127,'Epoch':0,'Pending':0,'Counts':dict.fromkeys(FIELDS,0),'Families':[[dict.fromkeys(FAMILY_FIELDS,0) for _ in range(10)] for _ in range(16)]} for i in range(4)]}
def repeats():
 d=fixture();o=d['Owners'][0];c=o['Counts'];c.update(Requests=5,Selected=5,FirstInWindow=2,RepeatedCompleted=2,NestedPending=1,Evictions=1,SameObservedState=2,FinishedFirst=1,FinishedRepeated=2,SameResult=1,ChangedResult=1,SameStateAndResult=1,EvictedBeforeFinish=1,RepeatedDescendantInstantiations=2)
 o['Families'][0][1].update({k:c[k] for k in FAMILY_FIELDS if k!='ZeroDescendantRepeats'});o['Families'][0][1]['ZeroDescendantRepeats']=1
 return d
class Counts(unittest.TestCase):
 def test_conservation_with_eviction(self):self.assertEqual(validate(repeats())['counts']['Requests'],5)
 def test_family_mismatch(self):
  d=repeats();d['Owners'][0]['Families'][0][1]['RepeatedDescendantInstantiations']=3
  with self.assertRaises(AssertionError):validate(d)
 def test_impossible_zero_descendants(self):
  d=repeats();o=d['Owners'][0];o['Counts']['RepeatedDescendantInstantiations']=0;o['Families'][0][1]['RepeatedDescendantInstantiations']=0
  with self.assertRaises(AssertionError):validate(d)
 def test_all_zero_descendants(self):
  d=repeats();d['Owners'][0]['Families'][0][1]['ZeroDescendantRepeats']=2
  with self.assertRaises(AssertionError):validate(d)
 def test_shape_and_names(self):
  d=fixture();d['Owners'][0]['Families'].pop()
  with self.assertRaises(AssertionError):validate(d)
  d=fixture();d['MapperFamilies'][1]='inference'
  with self.assertRaises(AssertionError):validate(d)
 def test_invalid_counts_and_pending(self):
  for value in [-1,True,1.5]:
   d=fixture();d['Owners'][0]['Families'][0][0]['Selected']=value
   with self.assertRaises(AssertionError):validate(d)
  d=fixture();d['Owners'][0]['Pending']=1
  with self.assertRaises(AssertionError):validate(d)
if __name__=='__main__':unittest.main()
