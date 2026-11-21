"""Isolate the 59 write guards without plan construction, lookup or reuse."""
from pathlib import Path
import hashlib
import json
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go/internal/checker"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
inventory = json.loads((here/"value-writes.json").read_text())
overlay = {}
for name, digest in inventory["files"].items():
    src = (root/name).read_bytes()
    assert hashlib.sha256(src).hexdigest()==digest
    for w in sorted((w for w in inventory["writes"] if w["File"]==name),key=lambda w:-w["Start"]):
        a,b=w["Start"],w["End"]
        assert src[a:b].startswith(w["Receiver"].encode()+b".resolvedType")
        src=src[:a]+f'{w["Checker"]}.setResolvedValue({w["Receiver"]}, {w["Value"]})'.encode()+src[b:]
    if name=="checker.go":
        src=src.replace(b"type Checker struct {",b"type Checker struct {\n absentPlans map[*Type]*absentPropertyPlan")
        src += b"""
type absentPropertyPlan struct {
    members []*ast.Symbol
    types []*Type
    spans []struct{start,end int}
}
func (c *Checker) setResolvedValue(links *ValueSymbolLinks, value *Type) {
    if links.watchesAbsentProperties && links.resolvedType != value {
        clear(c.absentPlans)
        links.watchesAbsentProperties = false
    }
    links.resolvedType = value
}
"""
    (out/name).write_bytes(src)
    overlay[str(root/name)]=str(out/name)
src=(root/"types.go").read_text()
field="functionOrConstructorChecked bool"
assert src.count(field)==1
(out/"types.go").write_text(src.replace(field,field+"\n watchesAbsentProperties bool"))
overlay[str(root/"types.go")]=str(out/"types.go")
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
