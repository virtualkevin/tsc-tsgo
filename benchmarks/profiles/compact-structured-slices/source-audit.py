from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=json.loads((p/'base.json').read_text());changes=json.loads((p/'changes.json').read_text());assert len(changes)==35
for rel,h in base.items():
 f=m/rel;assert sha(f)==h;s=f.read_text()
 if f.name=='types.go':
  for field,elem in [('properties','ast.Symbol'),('signatures','Signature'),('indexInfos','IndexInfo')]:
   s,n=re.subn(r'(\b'+field+r'\s+)\[\]\*'+re.escape(elem)+r'\b',r'\1compactSlice[*'+elem+']',s,count=1);assert n==1
 for c in changes:
  if c['file']==f.name:
   assert c['before']+'\n' in s;s=s.replace(c['before']+'\n',c['after']+'\n',1)
 formatted=subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=s.encode())
 assert formatted==(p/'staged'/f.name).read_bytes()
s=(p.parent/'compact-slice-header/prototype/slice.go').read_text().replace('package compactslice','package checker');s=re.sub(r'\bSlice\[','compactSlice[',s)
for old,new in [('From','compactSliceFrom'),('pack','packCompactSlice'),('indirectShape','compactSliceIndirectShape'),('indirect','indirectCompactSlice')]:s=re.sub(r'\b'+old+r'\b',new,s)
assert subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=s.encode())==(p/'staged/compact_slice.go').read_bytes()
s=(p/'staged/compact_structured_slices_test.go').read_text().replace('compactSliceFrom','baselineSliceIdentity').replace('.Values()','').replace('!= 16','!= 24')+'\nfunc baselineSliceIdentity[T any](s []T) []T {return s}\n'
assert s==(p/'baseline/compact_structured_slices_test.go').read_text()
paths=json.loads((p/'overlay.json').read_text())['Replace'];assert len(paths)==8
result={'passed':True,'base':base,'sources':{k:sha(v) for k,v in paths.items()},'changesSha256':sha(p/'changes.json'),'prototypeSourceSha256':sha(p.parent/'compact-slice-header/prototype/slice.go'),'controllerSha256':sha(__file__),'scope':'Exact replay of reviewed 35 access/write line adaptations and three field declarations. Prototype implementation identical modulo private names/package; baseline histories identical modulo storage representation and expected header size. This is source linkage, not a compiler proof.'}
(p/'source-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('Eight-file overlay and baseline histories reproduced exactly')
