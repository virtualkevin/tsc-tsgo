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
edit("internal/checker/checker.go", [(site,"""var apparentInput [2]atomic.Uint64
var heuristicWork [4][5]atomic.Uint64
func ApparentCounts() [22]uint64 {
    var out [22]uint64
    for i := range apparentInput {out[i] = apparentInput[i].Load()}
    for i := range heuristicWork {
        for j := range heuristicWork[i] {out[2+5*i+j] = heuristicWork[i][j].Load()}
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
    """+site+"""
    heuristicWork[group][0].Add(1)
    heuristicWork[group][1].Add(uint64(c.TotalInstantiationCount-inst))
    heuristicWork[group][2].Add(uint64(c.TypeCount-types))
    heuristicWork[group][3].Add(uint64(c.SymbolCount-symbols))
    heuristicWork[group][4].Add(uint64(len(resolved.properties)))""")])
edit("cmd/tsgo/main.go", [('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.ApparentCounts()); os.Exit(status)")])
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
