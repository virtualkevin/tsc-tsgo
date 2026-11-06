from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;m=p.parents[2]/'packages/tsc-go'
source=m/'internal/checker/checker.go';s=source.read_text()
anchor='func (c *Checker) getTypeOfPropertyOfType(t *Type, name string) *Type {\n'
assert s.count(anchor)==1
hook='\tif prop := cachedIntersectionProperty(t, name); prop != nil {\n\t\treturn c.getTypeOfSymbol(prop)\n\t}\n'
(p/'staged/checker.go').write_text(s.replace(anchor,anchor+hook))
paths={str(source):str(p/'staged/checker.go')};base={}
for name in ['fused_intersection_lookup.go','fused_intersection_lookup_test.go']:
 paths[str(m/'internal/checker'/name)]=str(p/'staged'/name)
for file in paths.values():subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',file],check=True)
base={'internal/checker/checker.go':hashlib.sha256(source.read_bytes()).hexdigest()}
(p/'base.json').write_text(json.dumps(base,indent=2)+'\n')
(p/'overlay.json').write_text(json.dumps({'Replace':paths},indent=2)+'\n')
# Baseline includes the same helper and tests, but never dispatches to it from production.
(p/'baseline-overlay.json').write_text(json.dumps({'Replace':{k:v for k,v in paths.items() if k!=str(source)}},indent=2)+'\n')
