"""Partition historical CPU under the innermost call resolver, never sum nested calls."""
from pathlib import Path
import collections,hashlib,json,re,sys,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
PREFIX='github.com/microsoft/typescript-go/internal/checker.(*Checker).'
BOUNDARIES={'resolveCall','resolveCallExpression','resolveNewExpression','resolveTaggedTemplateExpression'}
PHASES={'inferTypeArguments':'argument_inference','isSignatureApplicable':'applicability','getSignatureInstantiation':'signature_instantiation','getEffectiveCallArguments':'argument_preparation','reorderCandidates':'candidate_ordering','reportCallResolutionErrors':'error_reporting','getCandidateForOverloadFailure':'failure_recovery'}
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def decode(raw):
 sampletext,locs=raw.split('Locations\n',1);locs=locs.split('Mappings\n')[0];locations={};current=None
 for line in locs.splitlines():
  m=re.match(r'^\s*(\d+):\s+0x[0-9a-f]+(?:\s+M=\d+)?\s+(.*)',line)
  if m:current=int(m[1]);locations[current]=[];line=m[2]
  else:line=line.strip()
  if current is None:continue
  m=re.match(r'(.+?)\s+(\S+):(\d+):(\d+)(?:\s+s=\d+(?:\(.*\))?)?$',line)
  if m:locations[current].append((m[1],m[2],int(m[3])))
 for line in sampletext.splitlines():
  m=re.match(r'^\s+\d+\s+(\d+):\s*(.*)$',line)
  if not m:continue
  frames=[]
  for key in map(int,m[2].split()):
   assert key in locations and locations[key],('unparsed location',key)
   frames.extend(locations[key])
  yield int(m[1]),frames

def partition(samples,sites):
 total=0;call=0;phases=collections.Counter();passes=collections.Counter();cross=collections.Counter();boundaries=collections.Counter();lines=collections.Counter();choose=0;phase_lines=collections.Counter()
 for cpu,frames in samples:
  total+=cpu
  names=[f[0].removeprefix(PREFIX) if f[0].startswith(PREFIX) else '' for f in frames]
  indexes=[i for i,name in enumerate(names) if name in BOUNDARIES]
  if not indexes:continue
  call+=cpu;b=indexes[0];boundary=names[b];boundaries[boundary]+=cpu
  inner=names[:b];phase_index=next((i for i,n in enumerate(inner) if n in PHASES),None)
  nearest=PHASES[inner[phase_index]] if phase_index is not None else None
  if phase_index is not None:phase_lines[f'{inner[phase_index]}:{frames[phase_index][2]}']+=cpu
  has_choose='chooseOverload' in inner
  if has_choose:choose+=cpu
  phase=nearest or ('selection_other' if has_choose else 'call_body_other' if boundary=='resolveCall' else 'callee_or_dispatch')
  stage='not_choose_overload'
  if has_choose:
   stage=sites.get(frames[b][2],'unclassified_choose_site') if boundary=='resolveCall' else 'unclassified_choose_boundary'
  phases[phase]+=cpu;passes[stage]+=cpu;cross[phase+' / '+stage]+=cpu
  lines[f'{boundary}:{frames[b][2]}']+=cpu
 assert total>0 and sum(phases.values())==sum(passes.values())==sum(cross.values())==sum(boundaries.values())==call
 return {'totalCpuNs':total,'callCpuNs':call,'callPercent':100*call/total,'chooseOverloadCpuNs':choose,'chooseOverloadPercent':100*choose/total,'phaseNs':dict(sorted(phases.items())),'phasePercentTotal':{k:100*v/total for k,v in sorted(phases.items())},'passNs':dict(sorted(passes.items())),'passPercentTotal':{k:100*v/total for k,v in sorted(passes.items())},'phaseByPassNs':dict(sorted(cross.items())),'boundaryNs':dict(sorted(boundaries.items())),'boundarySourceLineNs':dict(sorted(lines.items())),'phaseSourceLineNs':dict(sorted(phase_lines.items()))}

def main():
 source=ROOT/'packages/tsc-go/internal/checker/checker.go';s=source.read_text();sites={}
 for i,line in enumerate(s.splitlines(),1):
  for expr,label in [('result = c.chooseOverload(&s, c.subtypeRelation)','subtype'),('result = c.chooseOverload(&s, c.assignableRelation)','assignable')]:
   if line.strip()==expr:assert label not in sites.values();sites[i]=label
 assert len(sites)==2
 assert sha(source)=='d9adabab3d6a26d44b42411f96522083fccca26c4eacda2131566549b4c1b760'
 base=P.parent/'normal-map-attribution';archive=base/'raw-profiles.tar.gz';inputs=json.loads((base/'inputs.json').read_text());prior=json.loads((P.parent/'initializer-work-budget/report.json').read_text());prior={p['project']:p for p in prior['projects']}
 manifest=json.loads((P.parent/'node-pointer-normal/manifest.json').read_text());rows=[]
 with tarfile.open(archive) as t:
  for e in inputs:
   data=t.extractfile(e['project']+'.raw.txt').read();assert hashlib.sha256(data).hexdigest()==e['rawSha256']
   assert manifest['files'][e['project']+'/'+Path(e['profile']).name]==e['profileSha256']
   result=partition(decode(data.decode()),sites);old=prior[e['project']]
   assert result['totalCpuNs']==old['totalCpuNs']
   assert abs(result['callPercent']-old['inclusivePercent']['call_resolution'])<1e-10
   rows.append({'project':e['project'],'profileSha256':e['profileSha256'],'rawSha256':e['rawSha256'],**result})
 report={'scope':'Offline historical CPU samples. Each sample belongs to its innermost selected call resolver and nearest listed inner phase, with chooseOverload fallback. Nested call work is not charged to an outer phase. Inclusive call total matches the prior call-resolution audit. Subtype/assignable labels identify sampled source callsites, not sequential retry counts, redundancy, semantic equivalence, removable CPU or wall-time forecasts. Other/unknown samples are retained. No compiler execution, timing or optimization.','sourceSha256':sha(source),'jsxSourceSha256':sha(ROOT/'packages/tsc-go/internal/checker/jsx.go'),'sites':sites,'phaseNames':PHASES,'archiveSha256':sha(archive),'inputsSha256':sha(base/'inputs.json'),'manifestSha256':sha(P.parent/'node-pointer-normal/manifest.json'),'priorSha256':sha(P.parent/'initializer-work-budget/report.json'),'analyzerSha256':sha(__file__),'projects':rows}
 text=json.dumps(report,indent=2)+'\n'
 if '--write' in sys.argv:(P/'report.json').write_text(text)
 else:assert (P/'report.json').read_text()==text
 for r in rows:print(r['project'],json.dumps({'callPercent':r['callPercent'],'phases':r['phasePercentTotal'],'passes':r['passPercentTotal']}))
if __name__=='__main__':main()
