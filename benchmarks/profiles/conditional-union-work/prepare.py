"""Observe existing visited entries, priorities and resolved conditional branches."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[3]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True,parents=True)
replacements = {}
def read(path):
    return subprocess.check_output(["git","show","8d9a8c3:packages/tsc-go/"+path],cwd=root,text=True)
def change(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old,new)
def save(path, s):
    dest = out/Path(path).name
    dest.write_text(s)
    replacements[str(root/path)] = str(dest)

path = "internal/checker/inference.go"
s = change(read(path), "import (", 'import (\n"sync/atomic"')
s = change(s, "type InferenceState struct {", "type InferenceState struct {\n mutationProbe uint32")
# Bits classify operations on the current inference state beneath a measured pair.
for marker, bit in [
    ("inference.candidates = nil", 2),
    ("if n.priority == inference.priority {", 4),
    ("inference.contraCandidates = append(inference.contraCandidates, candidate)", 8),
    ("inference.candidates = slices.Insert(inference.candidates, index, candidate)", 16),
    ("inference.topLevel = false", 32),
    ("inference.candidates = slices.Delete(inference.candidates, index, index+1)", 64),
]:
    old = marker
    add = f"if n.mutationProbe != 0 {{ n.mutationProbe |= {bit} }}"
    if marker.endswith("{"):
        new = marker + "\n" + add
    else:
        new = add + "\n" + marker
    s = change(s, old, new)
site = "matched := make([]bool, len(sources))"
s = change(s, site, site + "\n var branches map[[2]*Type]bool")
site = "c.inferFromTypes(n, sources[i], t)"
s = change(s, site, """wide := len(sources)>=32 && sources[i].flags&TypeFlagsObject != 0 && t.flags&TypeFlagsConditional != 0
					saveProbe := n.mutationProbe
                    if wide { n.mutationProbe = 1 }
                    var seen bool
					key := InferenceKey{s:sources[i].id, t:t.id}
					if wide { _,seen=n.visited[key] }
					""" + site + """
					if wide {
						mutationMasks[n.mutationProbe>>1].Add(1)
                        n.mutationProbe=saveProbe
                        index:=0
						if seen { index=1 }
						conditionalWork[index].Add(1)
						if _,ok:=n.visited[key];ok { conditionalWork[2].Add(1) }
						switch n.inferencePriority {
						case InferencePriorityMaxValue: conditionalWork[3].Add(1)
						case InferencePriorityCircularity: conditionalWork[4].Add(1)
						default: conditionalWork[5].Add(1)
						}
					}""")
site = "n.inferencePriority = min(n.inferencePriority, saveInferencePriority)\n\t\t\t\t}"
s = change(s, site, site + """
				if len(sources)>=32 && t.flags&TypeFlagsConditional != 0 {
					conditionalWork[6].Add(1)
					ct := t.AsConditionalType()
					if ct.resolvedTrueType != nil && ct.resolvedFalseType != nil {
						pair := [2]*Type{ct.resolvedTrueType,ct.resolvedFalseType}
						if branches == nil { branches=make(map[[2]*Type]bool) }
						if branches[pair] { conditionalWork[8].Add(1) } else { conditionalWork[7].Add(1); branches[pair]=true }
						if pair[0].flags&TypeFlagsStructuredOrInstantiable==0 && pair[1].flags&TypeFlagsStructuredOrInstantiable==0 {
							conditionalWork[9].Add(1)
						}
					}
				}""")
s += """
var conditionalWork [10]atomic.Uint64
var mutationMasks [64]atomic.Uint64
func ConditionalWorkCounts() map[string]any {
    var out [10]uint64
    var masks [64]uint64
    for i := range masks { masks[i]=mutationMasks[i].Load() }
	for i := range out { out[i] = conditionalWork[i].Load() }
	return map[string]any{"values":out, "masks":masks}
}
"""
save(path,s)
path="cmd/tsgo/main.go"
s=change(read(path),'"context"','"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
save(path,change(s,"os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.ConditionalWorkCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":replacements}))
