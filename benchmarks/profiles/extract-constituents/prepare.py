"""Trace intersection constituents of the wide conditional inferences."""
from pathlib import Path
import json
import sys
import subprocess
root=Path(__file__).resolve().parents[3]/'packages/tsc-go'
out=Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True,parents=True)
repls={}
def read(p):
    return subprocess.check_output(["git","show","8d9a8c3:packages/tsc-go/"+p],cwd=root,text=True)
def put(p,s):
    f=out/Path(p).name
    f.write_text(s)
    repls[str(root/p)]=str(f)
def edit(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
p="internal/checker/inference.go"
s=edit(read(p),"import (",'import (\n"sync/atomic"')
s=edit(s,"type InferenceState struct {","""type memberTrace struct {
    source, cond, part *Type
    bits int
}
type InferenceState struct {
    trace memberTrace""")
a="c.inferFromTypes(n, sources[i], t)"
s=edit(s,a,"if len(sources)>=32 && sources[i].flags&TypeFlagsObject!=0 && t.flags&TypeFlagsConditional!=0 { save:=n.trace; n.trace=memberTrace{source:sources[i],cond:t}; "+a+"; n.trace=save } else { "+a+" }")
begin=s.index("// We infer from types that are not naked type variables first")
end=s.index("// Inferences directly to naked type variables",begin)
sec=s[begin:end].replace("for _, t := range targets {","""var constituents []*Type
        if n.trace.cond!=nil && source==n.trace.source && n.trace.part==nil && targetFlags&TypeFlagsIntersection!=0 {
            branch:=n.trace.cond.AsConditionalType().resolvedTrueType
            if branch!=nil && branch.flags&TypeFlagsIntersection!=0 { constituents=branch.Types() }
        }
        measuring:=len(targets)>0 && len(targets)==len(constituents) && &targets[0]==&constituents[0]
        for i,t := range targets {""")
sec=edit(sec,"c.inferFromTypes(n, source, t)","""if measuring { n.trace.part=t; n.trace.bits=0 }
                c.inferFromTypes(n, source, t)
                if measuring { memberTraceCounts[min(i,7)][n.trace.bits].Add(1); n.trace.part=nil }""")
s=s[:begin]+sec+s[end:]
for site,bit in [
 ('if !c.couldContainTypeVariables(target) || c.isNoInferType(target) {',1),
 ('if status, ok := n.visited[key]; ok {',2),
 ('n.visited[key] = InferencePriorityCircularity',4),
 ('if c.typesDefinitelyUnrelated(source, target) {',8),
 ('c.inferFromProperties(n, source, target)',16),
 ('n.inferencePriority = min(n.inferencePriority, n.priority)',32)
]:
    # Property and relatedness markers are read only after their original checks.
    event=f'if source==n.trace.source && target==n.trace.part {{ n.trace.bits|={bit} }}'
    s=edit(s,site,site+'\n'+event)
s+="""
var memberTraceCounts [8][64]atomic.Uint64
func MemberTraceCounts() (out [8][64]uint64) {
    for i:=range out {for j:=range out[i] {out[i][j]=memberTraceCounts[i][j].Load()}}
    return out
}
"""
put(p,s)
p="cmd/tsgo/main.go"
s=edit(read(p),'"context"','"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
put(p,edit(s,"os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.MemberTraceCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":repls}))
