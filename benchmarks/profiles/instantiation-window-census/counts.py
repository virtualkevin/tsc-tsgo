FIELDS='Requests Aliased Unsampled Selected FirstInWindow RepeatedCompleted NestedPending Evictions SameObservedState ChangedObservedState FinishedFirst FinishedRepeated SameResult ChangedResult SameStateAndResult EvictedBeforeFinish FirstDescendantInstantiations RepeatedDescendantInstantiations CounterWraps'.split()
def validate(data):
 assert data['SchemaVersion']==1 and isinstance(data['Scope'],str)
 owners=data['Owners'];assert isinstance(owners,list) and len(owners)==4
 ids=set();total={k:0 for k in FIELDS};epochs=0
 for owner in owners:
  assert set(owner)=={'CheckerID','Slots','SamplingMask','Epoch','Pending','Counts'}
  for k in ('CheckerID','Slots','SamplingMask','Epoch','Pending'):assert type(owner[k]) is int and owner[k]>=0
  assert owner['CheckerID']>0 and owner['CheckerID'] not in ids;ids.add(owner['CheckerID'])
  assert owner['Slots']==4096 and owner['SamplingMask']==127 and owner['Pending']==0
  c=owner['Counts'];assert set(c)==set(FIELDS) and all(type(v) is int and v>=0 for v in c.values())
  assert c['Requests']==c['Aliased']+c['Unsampled']+c['Selected']
  assert c['Selected']==c['FirstInWindow']+c['RepeatedCompleted']+c['NestedPending']
  assert c['RepeatedCompleted']==c['SameObservedState']+c['ChangedObservedState']
  assert c['FirstInWindow']+c['RepeatedCompleted']==c['FinishedFirst']+c['FinishedRepeated']+c['EvictedBeforeFinish']
  assert c['FinishedFirst']<=c['FirstInWindow'] and c['FinishedRepeated']<=c['RepeatedCompleted']
  assert c['FinishedRepeated']==c['SameResult']+c['ChangedResult']
  assert c['SameStateAndResult']<=min(c['SameResult'],c['SameObservedState'])
  assert 0<=c['FirstInWindow']-c['Evictions']<=owner['Slots']
  assert c['CounterWraps']==0
  total={k:total[k]+c[k] for k in FIELDS};epochs+=owner['Epoch']
 return {'owners':len(owners),'invalidationEpochs':epochs,'counts':total,'limitation':'Hash-selected bounded windows; eviction censors repeats, partial state/result identity is not cache safety, descendant counts overlap and are not CPU or removable cost. No population extrapolation.'}
