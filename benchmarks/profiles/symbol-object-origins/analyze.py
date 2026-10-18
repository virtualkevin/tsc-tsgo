from pathlib import Path
import importlib.util,json,hashlib,collections,sys
root=Path(__file__).resolve().parents[3];here=Path(__file__).resolve().parent;heap=root/'benchmarks/profiles/completed-heap-census'
spec=importlib.util.spec_from_file_location('heap_parser',heap/'heap_parser.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
PREFIX='github.com/microsoft/typescript-go/internal/checker.(*Checker).'
TARGETS={'newSymbol':'symbol','newObjectType':'object'}
SKIP={'symbol':{'newSymbol','newSymbolEx','newInstantiatedSymbol','newInstantiatedSymbolWithLinks','instantiateSymbol','createSymbolWithType'},'object':{'newObjectType','newAnonymousType'}}
def classify(records):
 total=[0]*4;selected=[0]*4;groups=collections.defaultdict(lambda:[0]*4)
 for values,frames in records:
  total=[a+b for a,b in zip(total,values)]
  hit=next(((i,TARGETS[f.removeprefix(PREFIX)]) for i,f in enumerate(frames) if f.startswith(PREFIX) and f.removeprefix(PREFIX) in TARGETS),None)
  if hit is None:continue
  i,family=hit
  caller=next((f.removeprefix(PREFIX) for f in frames[i+1:] if f.startswith(PREFIX) and f.removeprefix(PREFIX) not in SKIP[family]),'<no outer checker caller>')
  groups[family,caller]=[a+b for a,b in zip(groups[family,caller],values)];selected=[a+b for a,b in zip(selected,values)]
 assert selected==[sum(v[i] for v in groups.values()) for i in range(4)]
 assert all(a<=b for a,b in zip(selected,total))
 metrics=lambda v:dict(zip(parser.METRICS,v))
 return {'allSamples':metrics(total),'selectedSamples':metrics(selected),'origins':[{'family':f,'caller':c,**metrics(v)} for (f,c),v in sorted(groups.items(),key=lambda x:(-x[1][3],x[0]))]}
def main():
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();decoded=json.loads((heap/'decoded.json').read_text());manifest=json.loads((heap/'manifest.json').read_text())['files']
 paths=[root/'packages/tsc-go/internal/checker/checker.go',root/'packages/tsc-go/internal/checker/types.go',root/'packages/tsc-go/internal/checker/pending_members.go',heap/'heap_parser.py',heap/'decoded.json']
 result={'scope':'Offline allocation-stack attribution from verified completed-work profiles. Each sample goes to its innermost selected constructor and first outer checker caller after listed wrappers. No repeated-request count, semantic-equivalence proof, retained ownership, or removable-time claim. Arena allocation objects are slabs, not numbers of symbols. Selected classes are disjoint; non-selected allocations remain in the denominator.','inputSha256':{str(p.relative_to(root)):sha(p) for p in paths},'skipWrappers':{k:sorted(v) for k,v in SKIP.items()},'projects':[]}
 for name in ['typeorm','trpc','vscode','sentry']:
  p=heap/name/'heap/after.raw.txt';h=sha(p);assert h==manifest[str(p.relative_to(heap))]['sha256']
  row=next(x for x in decoded['profiles'] if x['project']==name and x['phase']=='after');assert h==row['rawSha256']
  result['projects'].append({'project':name,'rawSha256':h,**classify(parser.parse(p.read_text()))})
 text=json.dumps(result,indent=2)+'\n'
 if '--write' in sys.argv:(here/'report.json').write_text(text)
 else:assert (here/'report.json').read_text()==text
 for p in result['projects']:print(p['project'],[(x['family'],x['caller'],round(x['inuseBytes']/1048576,2)) for x in p['origins'][:6]])
if __name__=='__main__':main()
