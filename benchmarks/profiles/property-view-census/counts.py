from pathlib import Path
import json
CATEGORIES=json.loads((Path(__file__).with_name('categories.json')).read_text())
def validate(data):
 assert data['SchemaVersion']==1 and data['Categories']==CATEGORIES
 assert isinstance(data['Owners'],list) and len(data['Owners'])==4
 ids=set();totals=[0]*19
 for owner in data['Owners']:
  assert set(owner)=={'CheckerID','Counts'}
  assert type(owner['CheckerID']) is int and owner['CheckerID']>0 and owner['CheckerID'] not in ids
  ids.add(owner['CheckerID']);c=owner['Counts']
  assert len(c)==19 and all(type(v) is int and v>=0 for v in c)
  assert c[2]<=c[1]<=c[0] and c[10]<=c[3]<=c[4] and c[10]<=c[17]
  assert c[11]==c[12]+c[13]+c[14]+c[15] and c[16]<=c[15]
  assert c[5]>=c[6]+c[7]+c[8]+c[9]
  totals=[a+b for a,b in zip(totals,c)]
 return {'owners':4,'categories':dict(zip(CATEGORIES,totals)),'entriesNotMaterializedAtSnapshot':totals[3]-totals[10],'entryMaterializationFraction':totals[10]/totals[3] if totals[3] else 0,'acceptedRelationFraction':totals[15]/totals[11] if totals[11] else 0,'limitation':'Counts are not CPU costs, liveness, permanent allocation savings, or speedup evidence.'}
