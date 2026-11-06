"""Validate completed observer accounting; bounded pair counts are not population estimates."""
def validate(report):
 assert report['SchemaVersion']==1 and report['Owners']
 totals={k:0 for k in ['Calls','True','TrackedFirst','TrackedRepeat','Dropped','ChangedResult','InclusiveInstantiations','ExclusiveInstantiations','InclusiveRelationGrowth','ExclusiveRelationGrowth','RepeatExclusiveInstantiations','RepeatExclusiveRelationGrowth']}
 ids=set()
 for owner in report['Owners']:
  assert not owner['Active'] and owner['CheckerID'] not in ids
  ids.add(owner['CheckerID'])
  assert owner['PairLimit']==131072 and 0<=owner['TrackedPairs']<=owner['PairLimit']
  keys=set();first=0
  for row in owner['Rows']:
   key=(row['SourceFlags'],row['TargetFlags'],row['ActiveContext'])
   assert key not in keys;keys.add(key)
   assert isinstance(row['ActiveContext'],bool)
   for k in totals:
    assert isinstance(row[k],int)
    if 'RelationGrowth' not in k:assert row[k]>=0
    totals[k]+=row[k]
   assert row['Calls']==row['TrackedFirst']+row['TrackedRepeat']+row['Dropped']
   assert row['True']<=row['Calls'] and row['ChangedResult']<=row['TrackedRepeat']
   assert row['RepeatExclusiveInstantiations']<=row['ExclusiveInstantiations']<=row['InclusiveInstantiations']
   first+=row['TrackedFirst']
  assert first==owner['TrackedPairs']
 return totals
