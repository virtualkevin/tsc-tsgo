"""Count apparent-type inputs and first resolutions requested during intersection reduction."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
overlay={}
def edit(file, changes):
    source=subprocess.check_output(["git","show","bd1baea:packages/tsc-go/"+file],cwd=root,text=True)
    for old,new in changes:
        assert source.count(old)==1
        source=source.replace(old,new)
    dest=out/Path(file).name
    dest.write_text(source)
    overlay[str(root/file)]=str(dest)
site="func (c *Checker) getReducedApparentType(t *Type) *Type {"
edit("internal/checker/checker.go", [
    ("type Checker struct {","""type Checker struct {
        heuristicResolutionDepth int
        heuristicMappedSymbols map[*ast.Symbol]uint8"""),
    ("addMemberForKeyTypeWorker := func(keyType *Type, propNameType *Type) {",
     "fromKeyof := false\n    addMemberForKeyTypeWorker := func(keyType *Type, propNameType *Type) {"),
    ("// We have a { [P in keyof T]: X }\n\t\tc.forEachMappedTypePropertyKeyTypeAndIndexSignatureKeyType(modifiersType, include,",
     "// We have a { [P in keyof T]: X }\n        fromKeyof = true\n        c.forEachMappedTypePropertyKeyTypeAndIndexSignatureKeyType(modifiersType, include,"),
    ("members[propName] = prop", """members[propName] = prop
        if c.heuristicResolutionDepth != 0 {
            if c.heuristicMappedSymbols == nil {c.heuristicMappedSymbols = make(map[*ast.Symbol]uint8)}
            if len(c.heuristicMappedSymbols) < 250_000 {
                var cohort uint8
                if nameType == nil && keyType == propNameType && keyType.flags == TypeFlagsStringLiteral {
                    cohort = 1
                    if fromKeyof {cohort = 2}
                }
                c.heuristicMappedSymbols[prop] = cohort
                mappedCohorts[cohort][0].Add(1)
                mappedDemand[0].Add(1)
            } else {mappedDemand[1].Add(1)}
        }"""),
    ("func (c *Checker) getTypeOfMappedSymbol(symbol *ast.Symbol) *Type {", """func (c *Checker) getTypeOfMappedSymbol(symbol *ast.Symbol) *Type {
        if cohort, seen := c.heuristicMappedSymbols[symbol]; seen && cohort < 3 {
            c.heuristicMappedSymbols[symbol] = cohort+3
            if c.heuristicResolutionDepth != 0 { mappedCohorts[cohort][1].Add(1) } else {mappedCohorts[cohort][2].Add(1)}
            if c.heuristicResolutionDepth != 0 { mappedDemand[2].Add(1) } else { mappedDemand[3].Add(1) }
        }"""),
    (site,"""var apparentInput [2]atomic.Uint64
var heuristicWork [4][8]atomic.Uint64
var mappedDemand [4]atomic.Uint64
var mappedCohorts [3][3]atomic.Uint64
func ApparentCounts() [47]uint64 {
    var out [47]uint64
    for i := range mappedCohorts {for j := range mappedCohorts[i] {out[38+3*i+j] = mappedCohorts[i][j].Load()}}
    for i := range mappedDemand {out[34+i] = mappedDemand[i].Load()}
    for i := range apparentInput {out[i] = apparentInput[i].Load()}
    for i := range heuristicWork {
        for j := range heuristicWork[i] {out[2+8*i+j] = heuristicWork[i][j].Load()}
    }
    return out
}
"""+site+"""
    if t.flags == TypeFlagsObject && t.objectFlags&ObjectFlagsMapped == 0 {
        apparentInput[0].Add(1)
    } else { apparentInput[1].Add(1) }""")])
site="resolved := c.resolveStructuredTypeMembers(apparent)"
edit("internal/checker/lazy_properties.go", [(site,"""group := 0
    if apparent.objectFlags&ObjectFlagsMembersResolved == 0 {
        switch {
        case apparent.objectFlags&ObjectFlagsReference != 0: group = 1
        case apparent.objectFlags&ObjectFlagsMapped != 0: group = 2
        default: group = 3
        }
    }
    inst,types,symbols := c.TotalInstantiationCount,c.TypeCount,c.SymbolCount
    c.heuristicResolutionDepth++
    """+site+"""
    c.heuristicResolutionDepth--
    heuristicWork[group][0].Add(1)
    heuristicWork[group][1].Add(uint64(c.TotalInstantiationCount-inst))
    heuristicWork[group][2].Add(uint64(c.TypeCount-types))
    heuristicWork[group][3].Add(uint64(c.SymbolCount-symbols))
    heuristicWork[group][4].Add(uint64(len(resolved.properties)))
    if c.TotalInstantiationCount != inst {heuristicWork[group][5].Add(1)}
    if c.SymbolCount-symbols >= 64 {heuristicWork[group][6].Add(1)}
    if c.SymbolCount-symbols >= 64 {heuristicWork[group][7].Add(uint64(c.SymbolCount-symbols))}""")])
edit("cmd/tsgo/main.go", [('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.ApparentCounts()); os.Exit(status)")])
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
