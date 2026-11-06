"""Disjoint attribution by the innermost contextual-type query's source line."""
from pathlib import Path
import collections,hashlib,importlib.util,json,re,sys,tarfile
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
PARSER=P.parent/'call-resolution-partition/analyze.py'
spec=importlib.util.spec_from_file_location('call_partition',PARSER);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
PREFIX=parser.PREFIX
QUERY=PREFIX+'getContextualType'

def partition(samples,sites):
 total=selected=0;stages=collections.Counter();lines=collections.Counter();flat=collections.defaultdict(collections.Counter);inclusive=collections.defaultdict(collections.Counter)
 for cpu,frames in samples:
  assert cpu>=0 and frames
  total+=cpu
  index=next((i for i,f in enumerate(frames) if f[0]==QUERY),None)
  if index is None:continue
  selected+=cpu;line=frames[index][2];stage=sites.get(str(line),'dispatch_or_unclassified')
  stages[stage]+=cpu;lines[str(line)]+=cpu;flat[stage][frames[0][0]]+=cpu
  for name in {f[0] for f in frames[:index]}:inclusive[stage][name]+=cpu
 assert sum(stages.values())==sum(lines.values())==selected
 assert sum(sum(x.values()) for x in flat.values())==selected
 ordered=lambda x:{k:dict(sorted(v.items())) for k,v in sorted(x.items())}
 return {'totalCpuNs':total,'selectedCpuNs':selected,'selectedPercent':100*selected/total,'stageNs':dict(sorted(stages.items())),'stagePercentTotal':{k:100*v/total for k,v in sorted(stages.items())},'queryLineNs':dict(sorted(lines.items())),'flatFunctionsByStage':ordered(flat),'inclusiveFunctionsByStage':ordered(inclusive)}

def source_sites(source):
 lines=source.splitlines();inside=False;sites={}
 for number,text in enumerate(lines,1):
  if text.startswith('func '):inside=text.startswith('func (c *Checker) getContextualType(')
  if not inside:continue
  calls=re.findall(r'c\.([A-Za-z0-9_]+)\(',text)
  if calls:
   assert len(calls)==1,(number,text)
   sites[str(number)]=calls[0]
 assert len(sites)==25,sites
 return sites

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 source=ROOT/'packages/tsc-go/internal/checker/checker.go';prior=json.loads((P.parent/'call-resolution-partition/report.json').read_text());assert sha(source)==prior['sourceSha256'];assert sha(PARSER)==prior['analyzerSha256'];sites=source_sites(source.read_text())
 base=P.parent/'normal-map-attribution';inputs=json.loads((base/'inputs.json').read_text());assert sha(base/'raw-profiles.tar.gz')==prior['archiveSha256'];assert sha(base/'inputs.json')==prior['inputsSha256']
 rows=[]
 with tarfile.open(base/'raw-profiles.tar.gz') as tar:
  for item,old in zip(inputs,prior['projects'],strict=True):
   assert item['project']==old['project'];raw=tar.extractfile(item['project']+'.raw.txt').read();assert hashlib.sha256(raw).hexdigest()==item['rawSha256']==old['rawSha256']
   row=partition(parser.decode(raw.decode()),sites);assert row['totalCpuNs']==old['totalCpuNs'];rows.append({'project':item['project'],'rawSha256':item['rawSha256'],**row})
 report={'scope':'Historical normal CPU samples, not wall time, duplicate queries, removable work or a speedup forecast. Each sample is assigned once to its innermost getContextualType source callsite. Recursive contexts are not double counted. Inclusive descendant rows overlap; flat and stage rows partition selected samples. Unknown lines stay explicit. No new compiler execution.','sourceSha256':sha(source),'parserSha256':sha(PARSER),'priorSha256':sha(P.parent/'call-resolution-partition/report.json'),'archiveSha256':sha(base/'raw-profiles.tar.gz'),'inputsSha256':sha(base/'inputs.json'),'analyzerSha256':sha(__file__),'sites':sites,'projects':rows}
 text=json.dumps(report,indent=2)+'\n'
 if '--write' in sys.argv:(P/'report.json').write_text(text)
 else:assert text==(P/'report.json').read_text()
 for row in rows:print(row['project'],json.dumps(row['stagePercentTotal']))
if __name__=='__main__':main()
