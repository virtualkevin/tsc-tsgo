"""Overlay a checker-local, observational cache for short ordered union inputs."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
paths = {}
def read(path):
    return subprocess.check_output(["git","show","e1eeaab:packages/tsc-go/"+path],cwd=root,text=True)
def save(path,text):
    dest = out / Path(path).name
    dest.write_text(text)
    paths[str(root/path)] = str(dest)
path = "internal/checker/checker.go"
s = read(path)
marker = "type Checker struct {"
assert s.count(marker)==1
s=s.replace(marker, marker+"\n unionObservation *[4096]unionObservedSlot")
marker = "\treturn c.getUnionTypeWorker(types, unionReduction, alias, origin)\n}"
assert s.count(marker)==1
s=s.replace(marker, """
    if len(types) < 2 || len(types) > 4 || alias != nil || origin != nil {
        unionOther.Add(1)
        return c.getUnionTypeWorker(types, unionReduction, alias, origin)
    }
    key := unionObservedKey{reduction: unionReduction}
    hash := uint32(unionReduction)+1
    pure := unionReduction != UnionReductionSubtype
    for i,t := range types {
        if t == nil {
            unionOther.Add(1)
            return c.getUnionTypeWorker(types, unionReduction, alias, origin)
        }
        key.types[i] = t
        hash = (hash ^ uint32(t.id)) * 16777619
        switch t.flags {
        case TypeFlagsString, TypeFlagsNumber, TypeFlagsBigInt, TypeFlagsBooleanLiteral, TypeFlagsStringLiteral,
             TypeFlagsNumberLiteral, TypeFlagsBigIntLiteral, TypeFlagsUndefined, TypeFlagsNull, TypeFlagsVoid, TypeFlagsNever:
            pure = pure && t.alias == nil && t.checker == c
        default: pure = false
        }
    }
    if c.unionObservation == nil { c.unionObservation = new([4096]unionObservedSlot) }
    slot := &c.unionObservation[(hash ^ hash >> 16) & 4095]
    prior := *slot
    before := c.TotalInstantiationCount
    result := c.getUnionTypeWorker(types, unionReduction, alias, origin)
    row := &unionRows[len(types)-2][0]
    if pure { row = &unionRows[len(types)-2][1] }
    row[0].Add(1)
    if prior.result != nil && prior.key == key {
        row[1].Add(1)
        if prior.result != result { row[2].Add(1) }
        if c.TotalInstantiationCount != before { row[3].Add(1) }
    }
    if result != c.errorType { *slot = unionObservedSlot{key,result} }
    return result
}

type unionObservedKey struct { types [4]*Type; reduction UnionReduction }
type unionObservedSlot struct { key unionObservedKey; result *Type }
var unionOther atomic.Uint64
var unionRows [3][2][4]atomic.Uint64
func UnionObservation() any {
    var rows [3][2][4]uint64
    for n := range rows { for k := range rows[n] { for j := range rows[n][k] {
        rows[n][k][j] = unionRows[n][k][j].Load()
    } } }
    return struct { Other uint64; Rows [3][2][4]uint64 }{unionOther.Load(),rows}
}""")
save(path,s)
path="cmd/tsgo/main.go"
s=read(path).replace('"context"','"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
assert s.count("os.Exit(runMain())")==1
save(path,s.replace("os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.UnionObservation()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":paths}))
