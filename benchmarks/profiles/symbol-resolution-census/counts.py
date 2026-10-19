"""Reject malformed/incomplete diagnostic snapshots; no semantic equivalence claims."""
import json
KINDS=['deferred','instantiated','mapped','reverse-mapped','accessor','variable-property','function-class-module','enum-member','alias']
def validate(report):
 assert report['SchemaVersion']==1 and report['Kinds']==KINDS
 ids=set();totals={'hits':0,'misses':0,'recorded':0,'dropped':0,'unresolvedCalls':0,'owners':len(report['Owners'])}
 for owner in report['Owners']:
  assert owner['CheckerID'] not in ids and not owner['Active'];ids.add(owner['CheckerID'])
  assert len(owner['Hits'])==len(owner['Misses'])==9
  assert all(type(x)==int and x>=0 for x in owner['Hits']+owner['Misses'])
  assert type(owner['DroppedOrigins'])==int and owner['DroppedOrigins']>=0
  recorded=[0]*9
  origins=owner['Origins'];assert len(origins)<=100000
  for key,r in origins.items():
   d=json.loads(key);assert 0<=d['Kind']<9 and r['Kind']==d['Kind']
   for field in ['Calls','Completed','Cached','ErrorResults','InclusiveNs','ExclusiveNs','InclusiveInstantiations','ExclusiveInstantiations']:
    assert type(r[field])==int and r[field]>=0
   assert r['Calls']>0 and r['Completed']<=r['Calls'] and r['Cached']<=r['Calls'] and r['ErrorResults']<=r['Completed']
   assert r['ExclusiveNs']<=r['InclusiveNs'] and r['ExclusiveInstantiations']<=r['InclusiveInstantiations']
   recorded[r['Kind']]+=r['Calls']
   if d['Unresolved']:totals['unresolvedCalls']+=r['Calls']
  assert all(x<=y for x,y in zip(recorded,owner['Misses']))
  assert sum(recorded)+owner['DroppedOrigins']==sum(owner['Misses'])
  if owner['DroppedOrigins']:assert len(origins)==100000
  totals['hits']+=sum(owner['Hits']);totals['misses']+=sum(owner['Misses']);totals['recorded']+=sum(recorded);totals['dropped']+=owner['DroppedOrigins']
 return totals
