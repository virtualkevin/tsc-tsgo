from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;m=p.parents[2]/'packages/tsc-go'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base=json.loads((p/'base.json').read_text());assert all(sha(k)==v for k,v in base.items())
s=(p/'staged/checker.go').read_text()
a='\tvar allPropertiesTable ast.SymbolTable\n';assert s.count(a)==1
s=s.replace(a,a+'\tif c.strictNullChecks {\n\t\tallPropertiesTable = make(ast.SymbolTable)\n\t}\n')
a='''		// Only spread override diagnostics consume this private table. Allocate
		// during the existing prepass so all preceding properties are recorded.
		if elem.Kind == ast.KindSpreadAssignment && c.strictNullChecks && allPropertiesTable == nil {
			allPropertiesTable = make(ast.SymbolTable)
		}
'''
assert s.count(a)==1;s=s.replace(a,'');assert s==(m/'internal/checker/checker.go').read_text()
paths=json.loads((p/'overlay.json').read_text())['Replace'];assert len(paths)==2
(p/'source-audit.json').write_text(json.dumps({'passed':True,'base':base,'sources':{k:sha(v) for k,v in paths.items()},'controllerSha256':sha(__file__),'scope':'Reversing the private table allocation relocation restores the entire original checker.go byte-for-byte.'},indent=2)+'\n')
print('Exact source inverse passed')
