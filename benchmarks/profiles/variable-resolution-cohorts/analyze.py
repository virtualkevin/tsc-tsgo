from pathlib import Path
import hashlib,json,re,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CENSUS=HERE.parent/'symbol-resolution-census'
sys.path.insert(0,str(CENSUS))
from artifacts import read_capture,digest
from counts import validate

def cohort(d,names):
 if d['Unresolved']:kind='unresolved'
 elif len(d['Declarations'] or [])!=1:kind='multiple-declarations'
 else:kind=names[d['Declarations'][0]['Kind']]
 return kind+(' / active-context' if d['InstantiationDepth'] or d['ActiveMappers'] else ' / zero-recorded-context')
def summarize(census,names):
 validate(census);groups={};origins={};misses=0;recorded=0
 for owner in census['Owners']:
  misses+=owner['Misses'][5]
  for key,r in owner['Origins'].items():
   if r['Kind']!=5:continue
   d=json.loads(key);name=cohort(d,names)
   group=groups.setdefault(name,dict(calls=0,completed=0,cached=0,errorResults=0,exclusiveNs=0,exclusiveInstantiations=0,repeatedOriginCalls=0,repeatedOriginExclusiveNs=0))
   for field,out in [('Calls','calls'),('Completed','completed'),('Cached','cached'),('ErrorResults','errorResults'),('ExclusiveNs','exclusiveNs'),('ExclusiveInstantiations','exclusiveInstantiations')]:group[out]+=r[field]
   recorded+=r['Calls']
   if not d['Unresolved']:origins.setdefault(key,[]).append(r)
 repeated=[]
 for key,records in origins.items():
  if len(records)<2:continue
  descriptor=json.loads(key)
  if cohort(descriptor,names).startswith('KindVariableDeclaration /'):
   repeated.append(dict(origin=descriptor,owners=len(records),calls=sum(r['Calls'] for r in records),exclusiveNs=sum(r['ExclusiveNs'] for r in records),errorResults=sum(r['ErrorResults'] for r in records)))
  group=groups[cohort(json.loads(key),names)]
  group['repeatedOriginCalls']+=sum(r['Calls'] for r in records)
  group['repeatedOriginExclusiveNs']+=sum(r['ExclusiveNs'] for r in records)
 assert recorded<=misses and sum(x['calls'] for x in groups.values())==recorded
 return dict(misses=misses,recorded=recorded,unrecorded=misses-recorded,groups=groups,topRepeatedVariables=sorted(repeated,key=lambda r:r['exclusiveNs'],reverse=True)[:10])
def main():
 kindfile=ROOT/'packages/tsc-go/internal/ast/kind_stringer_generated.go'
 names={int(value):name for name,value in re.findall(r'_ = x\[(Kind\w+)-(\d+)\]',kindfile.read_text())}
 assert names[170]=='KindParameter'
 capture=json.loads((CENSUS/'report-resumed.json').read_text());assert capture['status']=='passed'
 rows=[]
 for run in capture['runs']:
  if run['mode']!='enabled' or run['checkers']!=4:continue
  filename='4-census.json';data=read_capture(CENSUS/run['project']/filename)
  assert digest(data)==run['artifacts'][filename]['sha256']
  result=summarize(json.loads(data),names);rows.append(dict(project=run['project'],censusSha256=digest(data),**result))
  print(run['project'],'recorded',result['recorded'],'of',result['misses'])
  for name,g in sorted(result['groups'].items(),key=lambda kv:kv[1]['exclusiveNs'],reverse=True)[:6]:print(name,g)
 report=dict(scope='Retained variable/property miss origins in four-checker diagnostic captures. Large-workload cap losses are not random. Declaration kind describes the sole recorded declaration, not proof of annotation, flow, diagnostic, mapper or inference equivalence. Zero recorded context only means zero instantiation depth and active mapper count. Elapsed values are instrumented, not CPU or savings; repeated costs include first owner.',captureSha256=digest((CENSUS/'report-resumed.json').read_bytes()),kindSourceSha256=digest(kindfile.read_bytes()),projects=rows)
 (HERE/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
