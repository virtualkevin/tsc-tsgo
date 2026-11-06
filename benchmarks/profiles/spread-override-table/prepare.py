from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;m=p.parents[2]/'packages/tsc-go';src=m/'internal/checker/checker.go';s=src.read_text()
a='\tvar allPropertiesTable ast.SymbolTable\n\tif c.strictNullChecks {\n\t\tallPropertiesTable = make(ast.SymbolTable)\n\t}'
assert s.count(a)==1;s=s.replace(a,'\tvar allPropertiesTable ast.SymbolTable')
a='\tfor _, elem := range node.Properties() {\n\t\tif elem.Name() != nil && ast.IsComputedPropertyName(elem.Name()) {'
assert s.count(a)==1
s=s.replace(a,'''\tfor _, elem := range node.Properties() {
        // Only spread override diagnostics consume this private table. Allocate
        // during the existing prepass so all preceding properties are recorded.
        if elem.Kind == ast.KindSpreadAssignment && c.strictNullChecks && allPropertiesTable == nil {
            allPropertiesTable = make(ast.SymbolTable)
        }
\t\tif elem.Name() != nil && ast.IsComputedPropertyName(elem.Name()) {''')
dest=p/'staged/checker.go';dest.write_text(s)
paths={str(src):str(dest),str(m/'internal/checker/spread_override_table_api_test.go'):str(p/'staged/spread_override_table_api_test.go')}
for f in paths.values():subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',f],check=True)
(p/'base.json').write_text(json.dumps({str(src):hashlib.sha256(src.read_bytes()).hexdigest()},indent=2)+'\n')
(p/'overlay.json').write_text(json.dumps({'Replace':paths},indent=2)+'\n')
(p/'baseline-overlay.json').write_text(json.dumps({'Replace':{k:v for k,v in paths.items() if k!=str(src)}},indent=2)+'\n')
