"""Generate a diagnostic overlay for the last absent-discriminant list seen per JSX union."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
files = {}
revision = "67c1753"

def replace(file, edits):
    source = subprocess.check_output(["git", "show", revision + ":packages/tsc-go/" + file], cwd=root, text=True)
    for old, new in edits:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    dest = out / Path(file).name
    dest.write_text(source)
    files[str(root / file)] = str(dest)

replace("internal/checker/checker.go", [("type Checker struct {", """type jsxAbsentHistory struct {
    names string
    result *Type
}
type Checker struct {
    jsxHistory map[*Type]jsxAbsentHistory
    jsxLookupCount uint64""")])
lookup = "targetType := c.getTypeOfPropertyOrIndexSignatureOfType(types[i], discriminator.name(n))"
replace("internal/checker/relater.go", [(lookup, "c.jsxLookupCount++\n                " + lookup)])
call = "discriminated := c.discriminateTypeByDiscriminableItems(contextualType, discriminator)"
replace("internal/checker/jsx.go", [
    ('"iter"', '"iter"\n    "strconv"\n    "sync/atomic"'),
    ("type JsxFlags uint32", """var jsxAbsentCounts [5][10]atomic.Uint64
func JsxAbsentCounts() [5][10]uint64 {
    var out [5][10]uint64
    for i := range out {
        for j := range out[i] { out[i][j] = jsxAbsentCounts[i][j].Load() }
    }
    return out
}
type JsxFlags uint32"""),
    (call, """before := c.jsxLookupCount
    inst, types, symbols := c.TotalInstantiationCount, c.TypeCount, c.SymbolCount
    assignable, subtype := c.assignableRelation.size(), c.subtypeRelation.size()
    active := c.instantiationDepth != 0 || len(c.activeMappers) != 0
    """ + call + """
    group := 0 // explicit discriminator value
    changed := false
    if len(discriminantProperties) == 0 {
        if len(discriminantMembers) == 0 {
            group = 1
        } else {
            if c.jsxHistory == nil { c.jsxHistory = make(map[*Type]jsxAbsentHistory) }
            var key []byte
            for _, member := range discriminantMembers { key = strconv.AppendQuote(key, member.Name) }
            names := string(key)
            last, seen := c.jsxHistory[contextualType]
            group = 2 // first absent-only request for this type
            if seen {
                group = 3 // different sequence of absent names
                if last.names == names {
                    group = 4
                    changed = last.result != discriminated
                }
            }
            c.jsxHistory[contextualType] = jsxAbsentHistory{names, discriminated}
        }
    }
    jsxAbsentCounts[group][0].Add(1)
    jsxAbsentCounts[group][1].Add(c.jsxLookupCount-before)
    if changed { jsxAbsentCounts[group][2].Add(1) }
    if discriminated != contextualType { jsxAbsentCounts[group][3].Add(1) }
    if c.TotalInstantiationCount != inst { jsxAbsentCounts[group][4].Add(1) }
    if c.TypeCount != types { jsxAbsentCounts[group][5].Add(1) }
    if c.SymbolCount != symbols { jsxAbsentCounts[group][6].Add(1) }
    if c.assignableRelation.size() != assignable { jsxAbsentCounts[group][7].Add(1) }
    if c.subtypeRelation.size() != subtype { jsxAbsentCounts[group][8].Add(1) }
    if active { jsxAbsentCounts[group][9].Add(1) }""")
])
replace("cmd/tsgo/main.go", [
    ('"context"', '"context"\n    "encoding/json"\n    "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.JsxAbsentCounts()); os.Exit(status)")
])
(out / "overlay.json").write_text(json.dumps({"Replace": files}))
