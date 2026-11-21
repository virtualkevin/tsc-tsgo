"""Build an isolated checker-local cache for ordered pairs of plain scalar types."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
path = Path("packages/tsc-go/internal/checker/checker.go")
s = subprocess.check_output(["git","show",f"e1eeaab:{path}"],cwd=root,text=True)
anchor = "type Checker struct {"
assert s.count(anchor)==1
s = s.replace(anchor,anchor+"\n scalarUnionPairs *[1024]scalarUnionPair")
anchor = "\treturn c.getUnionTypeWorker(types, unionReduction, alias, origin)\n}"
assert s.count(anchor)==1
s = s.replace(anchor,"""    if len(types) == 2 && unionReduction == UnionReductionLiteral && alias == nil && origin == nil {
        a, b := types[0], types[1]
        if plainScalarUnionInput(c,a) && plainScalarUnionInput(c,b) {
            if c.scalarUnionPairs == nil { c.scalarUnionPairs = new([1024]scalarUnionPair) }
            hash := (uint32(a.id)*16777619 ^ uint32(b.id)) * 16777619
            slot := &c.scalarUnionPairs[(hash ^ hash>>16) & 1023]
            if slot.a == a && slot.b == b { return slot.result }
            result := c.getUnionTypeWorker(types,unionReduction,nil,nil)
            *slot = scalarUnionPair{a,b,result}
            return result
        }
    }
""" + anchor + """

type scalarUnionPair struct { a,b,result *Type }

func plainScalarUnionInput(c *Checker, t *Type) bool {
    if t == nil || t.checker != c || t.alias != nil { return false }
    switch t.flags {
    case TypeFlagsString, TypeFlagsNumber, TypeFlagsBigInt, TypeFlagsBooleanLiteral, TypeFlagsStringLiteral,
         TypeFlagsNumberLiteral, TypeFlagsBigIntLiteral, TypeFlagsUndefined, TypeFlagsNull, TypeFlagsVoid, TypeFlagsNever:
         return true
    }
    return false
}
""")
target = out / "checker.go"
target.write_text(s)
files = {str(root/path):str(target)}
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
files[str(root/"packages/tsc-go/internal/checker/scalar_union_pairs_test.go")] = str(Path(__file__).with_name("pairs_test.go.txt").resolve())
(out/"test-overlay.json").write_text(json.dumps({"Replace":files}))
