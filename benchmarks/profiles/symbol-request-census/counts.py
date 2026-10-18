FIELDS=['Requests','NewKeys','RepeatedSameObservedState','RepeatedChangedObservedState','UntrackedAtCapacity']
KINDS=['nil','simple','array','merged','unknown']
def validate(data):
 assert data['SchemaVersion']==1 and data['MapperKinds']==KINDS
 owners=data['Owners'];assert isinstance(owners,list) and len(owners)==4
 ids=set();totals={k:0 for k in FIELDS};byKind=[{k:0 for k in FIELDS} for _ in KINDS]
 for owner in owners:
  assert isinstance(owner['CheckerID'],int) and owner['CheckerID']>0 and owner['CheckerID'] not in ids;ids.add(owner['CheckerID'])
  assert owner['Limit']==32768 and 0<=owner['TrackedKeys']<=owner['Limit']
  assert len(owner['Counts'])==5
  new=0
  for i,row in enumerate(owner['Counts']):
   assert set(row)==set(FIELDS) and all(type(v) is int and v>=0 for v in row.values())
   assert row['Requests']==sum(row[k] for k in FIELDS[1:])
   new+=row['NewKeys']
   if row['UntrackedAtCapacity']:assert owner['TrackedKeys']==owner['Limit']
   for k in FIELDS:totals[k]+=row[k];byKind[i][k]+=row[k]
  assert new==owner['TrackedKeys']
 return {'owners':len(owners),'totals':totals,'byMapperKind':[{'kind':k,**v} for k,v in zip(KINDS,byKind)],'limitation':'Counts concern a bounded first-key ledger and selected last-observed state, not safe reuse or population repetition rates. Unknown-at-capacity requests remain unknown.'}
