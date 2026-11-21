"""Attribute existing priority propagation to the two resolved conditional branches."""
from pathlib import Path
import json
import subprocess
import sys

root=Path(__file__).resolve().parents[3]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
overlay={}
def read(path):
    return subprocess.check_output(["git","show","8d9a8c3:packages/tsc-go/"+path],cwd=root,text=True)
def edit(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
def save(path,s):
    f=out/Path(path).name
    f.write_text(s)
    overlay[str(root/path)]=str(f)
path="internal/checker/inference.go"
s=edit(read(path),"import (",'import (\n"sync/atomic"')
s=edit(s,"type InferenceState struct {","""type branchObservation struct {
	source,target *Type
	pending bool
	branch int
	mask [2]uint8
}
type InferenceState struct {
	observe branchObservation""")
site="c.inferFromTypes(n, sources[i], t)"
s=edit(s,site,"""if len(sources)>=32 && sources[i].flags&TypeFlagsObject!=0 && t.flags&TypeFlagsConditional!=0 {
						save:=n.observe
						n.observe=branchObservation{source:sources[i],target:t}
						"""+site+"""
						branchMasks[n.observe.mask[0]][n.observe.mask[1]].Add(1)
						n.observe=save
					} else { """+site+" }")
site="c.inferToMultipleTypesWithPriority(n, source, targetTypes, target.flags,"
s=edit(s,site,"if source==n.observe.source && target==n.observe.target { n.observe.pending=true }; "+site)
site="typeVariableCount := 0"
s=edit(s,site,"direct:=n.observe.pending; n.observe.pending=false; "+site)
begin=s.index("// We infer from types that are not naked type variables first")
end=s.index("func getSingleTypeVariable",begin)
section=s[begin:end].replace("for _, t := range targets {","for i, t := range targets {")
for site in ["c.inferFromTypes(n, source, t)","c.inferWithPriority(n, source, t, InferencePriorityNakedTypeVariable)"]:
    section=edit(section,site,"if direct { n.observe.branch=i+1 }; "+site+"; if direct { n.observe.branch=0 }")
s=s[:begin]+section+s[end:]
site="n.inferencePriority = min(n.inferencePriority, n.priority)"
s=edit(s,site,"""if i:=n.observe.branch; i>0 {
                switch {case inference.isFixed: n.observe.mask[i-1]|=1
                case n.priority>inference.priority: n.observe.mask[i-1]|=2
                default: n.observe.mask[i-1]|=4}
            }
            """+site)
site="n.inferencePriority = min(n.inferencePriority, status)"
s=edit(s,site,"if i:=n.observe.branch;i>0 && status!=InferencePriorityMaxValue { n.observe.mask[i-1]|=8 }; "+site)
s+="""
var branchMasks [16][16]atomic.Uint64
func BranchCounts() (rows [16][16]uint64) {
	for i:=range rows {for j:=range rows[i] {rows[i][j]=branchMasks[i][j].Load()}}
	return rows
}
"""
save(path,s)
path="cmd/tsgo/main.go"
s=edit(read(path),'"context"','"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
save(path,edit(s,"os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.BranchCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
