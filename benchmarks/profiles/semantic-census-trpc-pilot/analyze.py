from pathlib import Path
import re,json,hashlib,collections,sys
O=Path(sys.argv[1]); result={'scope':'Sampled instrumented CPU only; no equivalent-result or removable-work claim','runs':[]}
for path in sorted(O.glob('*-profiles/cpu.raw.txt')):
 name=path.parent.name.removesuffix('-profiles');census=O/(name+'.census.jsonl');owners={}
 if census.exists():
  rows=[json.loads(l) for l in census.read_text().splitlines()][1:]
  owners={str(r['checkerId']):r for r in rows}
 text=path.read_text().split('Samples:\n',1)[1].split('Locations\n',1)[0]; samples=[]
 for line in text.splitlines():
  m=re.match(r'^\s+(\d+)\s+(\d+):',line)
  if m:samples.append({'count':int(m[1]),'cpu':int(m[2]),'labels':{}})
  elif 'census_' in line:
   labels=dict(re.findall(r'(census_\w+):\[([^\]]+)\]',line));assert set(labels)=={'census_checker','census_family','census_record'}
   samples[-1]['labels']=labels
 totals=collections.Counter();tagged=0;overflow=0
 for s in samples:
  if not s['labels']:continue
  l=s['labels'];owner=owners[l['census_checker']];key=l['census_record'];record=owner['overflow'] if key=='overflow' else owner['records'][int(key)]
  assert record['Family']==l['census_family'];assert record['Calls']>0
  totals[l['census_family']]+=s['cpu'];tagged+=s['cpu']
  if key=='overflow':overflow+=s['cpu']
 total=sum(s['cpu'] for s in samples);assert total>0
 if name.endswith('-labeled'):assert tagged>0
 else:assert tagged==0
 item={'name':name,'totalCpuNs':total,'taggedCpuNs':tagged,'overflowCpuNs':overflow,'familyCpuNs':dict(totals),'rawSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'jointLabelReferencesValid':True}
 if owners:
  calls=sum(sum(r['Calls'] for r in o['records'])+o['overflow']['Calls'] for o in owners.values()); oc=sum(o['overflow']['Calls'] for o in owners.values());item['overflowCallFraction']=oc/calls
 result['runs'].append(item)
(O/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
