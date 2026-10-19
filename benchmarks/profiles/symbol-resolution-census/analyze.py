"""Describe repeated origins; never label them equivalent or reusable results."""
from pathlib import Path
import hashlib,json
from counts import KINDS,validate
from artifacts import read_capture,digest
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def summarize(census):
 totals=validate(census)
 kinds=[dict(kind=k,hits=0,misses=0,recordedCalls=0,completed=0,cached=0,errorResults=0,exclusiveNs=0,exclusiveInstantiations=0,unresolvedCalls=0,repeatedOriginDescriptors=0,repeatedOriginCalls=0,repeatedOriginExclusiveNs=0) for k in KINDS]
 origins={}
 for owner in census['Owners']:
  for i,row in enumerate(kinds):row['hits']+=owner['Hits'][i];row['misses']+=owner['Misses'][i]
  for key,r in owner['Origins'].items():
   d=json.loads(key);row=kinds[r['Kind']]
   for out,field in [('recordedCalls','Calls'),('completed','Completed'),('cached','Cached'),('errorResults','ErrorResults'),('exclusiveNs','ExclusiveNs'),('exclusiveInstantiations','ExclusiveInstantiations')]:row[out]+=r[field]
   if d['Unresolved']:
    row['unresolvedCalls']+=r['Calls'];continue
   origins.setdefault(key,[]).append((owner['CheckerID'],r))
 for key,entries in origins.items():
  if len(entries)<2:continue
  assert len({o for o,_ in entries})==len(entries)
  row=kinds[json.loads(key)['Kind']];row['repeatedOriginDescriptors']+=1
  row['repeatedOriginCalls']+=sum(r['Calls'] for _,r in entries)
  row['repeatedOriginExclusiveNs']+=sum(r['ExclusiveNs'] for _,r in entries)
 return {'totals':totals,'originCoverageComplete':totals['dropped']==0,'recordedMissFraction':totals['recorded']/totals['misses'] if totals['misses'] else 1.0,'kinds':kinds}
def main():
 capture=json.loads((HERE/'report-resumed.json').read_text());assert capture['status']=='passed'
 rows=[]
 for run in capture['runs']:
  if run['mode']!='enabled':continue
  name=f"{run['checkers']}-census.json";f=HERE/run['project']/name
  data=read_capture(f);assert digest(data)==run['artifacts'][name]['sha256']
  census=json.loads(data);summary=summarize(census)
  assert summary['totals']==run['counts']
  rows.append({'project':run['project'],'requestedCheckers':run['checkers'],'censusSha256':digest(data),**summary})
 report={'scope':'Origin repetition only: equal full declaration/context-shape descriptors across checker owners, excluding unresolved origins. No mapper/inference/flow/diagnostic/result equivalence established. Repeated-origin costs include all matching owners, including the first; these are not avoidable work. Exclusive values partition observed nested resolver intervals but are instrumented elapsed time, not sampled CPU. Origin cap losses are reported. Retained origins are first-seen, not a random sample; do not extrapolate their costs or repetition rates. No speedup or safe sharing claim.','captureSha256':sha(HERE/'report-resumed.json'),'projects':rows}
 (HERE/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
 for row in rows:print(row['project'],row['requestedCheckers'],row['totals'])
if __name__=='__main__':main()
