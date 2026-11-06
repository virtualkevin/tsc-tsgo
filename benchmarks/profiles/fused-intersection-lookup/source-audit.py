from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;m=p.parents[2]/'packages/tsc-go';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=json.loads((p/'base.json').read_text());assert all(sha(m/k)==v for k,v in base.items())
s=(p/'staged/checker.go').read_text();hook='\tif prop := cachedIntersectionProperty(t, name); prop != nil {\n\t\treturn c.getTypeOfSymbol(prop)\n\t}\n'
assert s.count(hook)==1 and s.replace(hook,'',1)==(m/'internal/checker/checker.go').read_text()
a=json.loads((p/'overlay.json').read_text())['Replace'];b=json.loads((p/'baseline-overlay.json').read_text())['Replace']
assert len(a)==3 and b=={k:v for k,v in a.items() if k!=str(m/'internal/checker/checker.go')}
(p/'source-audit.json').write_text(json.dumps({'passed':True,'base':base,'sources':{k:sha(v) for k,v in a.items()},'baselineSources':{k:sha(v) for k,v in b.items()},'controllerSha256':sha(__file__),'scope':'Removing the single guarded entry dispatch reproduces checker.go exactly. All original fallback, reduction, cache population and symbol type query code remain unchanged. Baseline includes identical helper/tests but does not dispatch to it.'},indent=2)+'\n')
print('Exact fallback source and baseline correspondence verified')
