"""Validate all-row accounting without extrapolating bounded request histories."""
SCALARS=['Calls','NonNil','TrackedFirst','TrackedRepeat','Dropped','ChangedResult','InclusiveRelationGrowth','ExclusiveRelationGrowth','RepeatRelationGrowth','InclusiveNs','ExclusiveNs','InferenceSitesBefore','InferenceSitesAfter','ChangedInferenceFlags']
ARRAYS=['Inclusive','Exclusive','RepeatExclusive']
def validate(report):
 assert report['SchemaVersion']==1 and report['Owners']
 totals={k:0 for k in SCALARS};totals.update({k:[0,0,0] for k in ARRAYS});ids=set()
 for owner in report['Owners']:
  assert not owner['Active'] and owner['CheckerID'] not in ids;ids.add(owner['CheckerID'])
  assert owner['RequestLimit']==131072 and 0<=owner['TrackedRequests']<=131072
  first=0;keys=set()
  for row in owner['Rows']:
   key=tuple(row[k] for k in ['NodeKind','Mode','ContextFlags','HasInference','ActiveContext']);assert key not in keys;keys.add(key)
   assert isinstance(row['HasInference'],bool) and isinstance(row['ActiveContext'],bool)
   for k in SCALARS:
    assert type(row[k])==int
    if 'RelationGrowth' not in k:assert row[k]>=0
    totals[k]+=row[k]
   for k in ARRAYS:
    assert len(row[k])==3 and all(type(x)==int and x>=0 for x in row[k])
    for i,x in enumerate(row[k]):totals[k][i]+=x
   assert row['Calls']==row['TrackedFirst']+row['TrackedRepeat']+row['Dropped']
   assert row['NonNil']<=row['Calls'] and row['ChangedResult']<=row['TrackedRepeat'] and row['ChangedInferenceFlags']<=row['Calls']
   assert row['ExclusiveNs']<=row['InclusiveNs']
   for i in range(3):assert row['RepeatExclusive'][i]<=row['Exclusive'][i]<=row['Inclusive'][i]
   if not row['HasInference']:assert row['InferenceSitesBefore']==row['InferenceSitesAfter']==row['ChangedInferenceFlags']==0
   first+=row['TrackedFirst']
  assert first==owner['TrackedRequests']
 return totals
