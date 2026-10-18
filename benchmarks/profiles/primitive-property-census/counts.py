CATEGORIES=['non-plain-property','checker-metadata','declaration-identity','non-property-signature-or-parent','javascript','missing-annotation-or-initializer','non-closed-keyword','syntactic-candidate']
def validate(data):
 assert data['SchemaVersion']==1 and data['Categories']==CATEGORIES
 owners=data['Owners'];assert isinstance(owners,list) and len(owners)==4
 ids=set();totals=[0]*8
 for owner in owners:
  assert set(owner)=={'CheckerID','Counts'}
  assert type(owner['CheckerID']) is int and owner['CheckerID']>0 and owner['CheckerID'] not in ids;ids.add(owner['CheckerID'])
  assert len(owner['Counts'])==8 and all(type(x) is int and x>=0 for x in owner['Counts'])
  totals=[a+b for a,b in zip(totals,owner['Counts'])]
 total=sum(totals)
 return {'owners':len(owners),'constructorRequests':total,'syntacticCandidates':totals[7],'candidateFraction':totals[7]/total if total else 0,'categories':dict(zip(CATEGORIES,totals)),'limitation':'Ordered classification at clone construction, not all instantiation requests, cost, safe-reuse proof, or saved allocations. Frozen pending decisions may precede construction.'}
