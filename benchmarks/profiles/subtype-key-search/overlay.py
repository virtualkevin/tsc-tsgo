"""Observe repeated first-unit-property searches during subtype reduction."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
source_revision = "a261586"
base = root / "packages/tsc-go"
checker = base / "internal/checker/checker.go"
main = base / "cmd/tsgo/main.go"
def source(p):
    return subprocess.check_output(["git","show",source_revision+":"+str(p.relative_to(root))],cwd=root,text=True)

s = source(checker)
declaration = """type subtypeKeyObservation struct {
    key *ast.Symbol
    typ *Type
}
var subtypeKeyCounts [11]atomic.Uint64
func SubtypeKeyCounts() []uint64 {
    counts := make([]uint64,len(subtypeKeyCounts))
    for i := range counts { counts[i] = subtypeKeyCounts[i].Load() }
    return counts
}
type Checker struct {
    subtypeKeyFirst map[*Type]subtypeKeyObservation
"""
site = "keyProperty = core.Find(c.getPropertiesOfType(source), func(p *ast.Symbol) bool {"
end = "keyPropertyType = c.getRegularTypeOfLiteralType(c.getTypeOfSymbol(keyProperty))\n\t\t\t}"
assert s.count(site) == s.count(end) == 1
s=s.replace("type Checker struct {",declaration)
s=s.replace("var keyProperty *ast.Symbol\n\t\t\tvar keyPropertyType *Type",
            "var keyProperty *ast.Symbol\n\t\t\tvisited := uint64(0)\n\t\t\tbefore := c.TotalInstantiationCount\n\t\t\tvar searched bool\n\t\t\tvar keyPropertyType *Type")
s=s.replace(site,"searched = true\n"+site+"\nvisited++")
s=s.replace(end,end+"""
            if searched {
                subtypeKeyCounts[0].Add(1)
                subtypeKeyCounts[1].Add(visited)
                if c.subtypeKeyFirst == nil { c.subtypeKeyFirst = make(map[*Type]subtypeKeyObservation) }
                observation := subtypeKeyObservation{keyProperty,keyPropertyType}
                if first, ok := c.subtypeKeyFirst[source]; ok {
                    subtypeKeyCounts[2].Add(1)
                    subtypeKeyCounts[3].Add(visited)
                    if first == observation { subtypeKeyCounts[4].Add(1) }
                    if before != c.TotalInstantiationCount { subtypeKeyCounts[5].Add(1) }
                    if first.key == nil && keyProperty == nil { subtypeKeyCounts[6].Add(1) }
                } else {
                    c.subtypeKeyFirst[source] = observation
                }
                if keyProperty != nil { subtypeKeyCounts[7].Add(1) }
                if visited == 0 { subtypeKeyCounts[8].Add(1) }
                if before != c.TotalInstantiationCount { subtypeKeyCounts[9].Add(1) }
            }""")
skip="c.getRegularTypeOfLiteralType(t) != keyPropertyType {\n\t\t\t\t\t\t\tcontinue"
assert s.count(skip)==1
s=s.replace(skip,skip.replace("continue","subtypeKeyCounts[10].Add(1); continue"))
(out/checker.name).write_text(s)
s=source(main).replace('"context"', '"context"\n "fmt"\n "github.com/microsoft/typescript-go/internal/checker"')
s=s.replace("os.Exit(runMain())","status := runMain(); fmt.Fprintln(os.Stderr,checker.SubtypeKeyCounts()); os.Exit(status)")
(out/main.name).write_text(s)
(out/"overlay.json").write_text(json.dumps({"Replace":{str(p):str(out/p.name) for p in (checker,main)}}))
