BRANCHES=['unclassified','for-in','for-of','binding-element','catch','annotation','auto','auto-array','parameter-no-symbol','accessor-this','accessor-return','full-signature','contextual-parameter','initializer','instance-flow-or-base','static-flow-or-base','jsx-boolean','binding-pattern','no-inferred-type']
def validate(report):
 assert report['SchemaVersion']==1 and report['Branches']==BRANCHES
 owners=set();totals={'owners':len(report['Owners']),'calls':0,'nonNil':0,'errorResults':0,'exclusiveNs':0,'exclusiveInstantiations':0,'branchCalls':[0]*len(BRANCHES)}
 for owner in report['Owners']:
  assert not owner['Active'] and owner['CheckerID'] not in owners;owners.add(owner['CheckerID']);keys=set()
  for row in owner['Rows']:
   key=tuple(row[k] for k in ['Branch','DeclarationKind','CheckMode','IncludeOptionality','ActiveContext'])
   assert key not in keys;keys.add(key)
   assert type(row['Branch'])==int and 0<row['Branch']<len(BRANCHES)
   assert type(row['DeclarationKind'])==int and row['DeclarationKind']>=0
   assert type(row['CheckMode'])==int and row['CheckMode']>=0
   assert type(row['IncludeOptionality'])==bool and type(row['ActiveContext'])==bool
   for field in ['Calls','NonNil','ErrorResults','InclusiveNs','ExclusiveNs','InclusiveInstantiations','ExclusiveInstantiations']:assert type(row[field])==int and row[field]>=0
   assert 0<row['Calls'] and row['ErrorResults']<=row['NonNil']<=row['Calls']
   assert row['ExclusiveNs']<=row['InclusiveNs'] and row['ExclusiveInstantiations']<=row['InclusiveInstantiations']
   for dest,source in [('calls','Calls'),('nonNil','NonNil'),('errorResults','ErrorResults'),('exclusiveNs','ExclusiveNs'),('exclusiveInstantiations','ExclusiveInstantiations')]:totals[dest]+=row[source]
   totals['branchCalls'][row['Branch']]+=row['Calls']
 assert sum(totals['branchCalls'])==totals['calls'];return totals
