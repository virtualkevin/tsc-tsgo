"""Observe the existing inference guard and the three union matching passes."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = {}

def read(path):
    return subprocess.check_output(["git", "show", f"a6444de:packages/tsc-go/{path}"], cwd=root, text=True)

def replace(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)

def stage(path, source):
    file = out / Path(path).name
    file.write_text(source)
    overlay[str(root / path)] = str(file)

path = "internal/checker/inference.go"
s = replace(read(path), "import (", 'import (\n"sync/atomic"')
entry = "func (c *Checker) inferFromTypes(n *InferenceState, source *Type, target *Type) {"
s = replace(s, entry, entry + """
	c.inferFromTypesObserved(n, source, target, -1)
}
func (c *Checker) inferFromTypesObserved(n *InferenceState, source *Type, target *Type, width int) {""")
guard = "if !c.couldContainTypeVariables(target) || c.isNoInferType(target) {"
s = replace(s, guard, guard + """
		if width >= 0 { inferenceWork[width][2].Add(1) }""")
site = "c.inferFromTypes(n, sources[i], t)"
s = replace(s, site, "c.inferFromTypesObserved(n, sources[i], t, bucket)")
site = "for i := range sources {\n\t\t\t\t\tsaveInferencePriority"
s = replace(s, site, """bucket := inferenceWidth(len(sources))
				inferenceWork[bucket][0].Add(1)
				inferenceWork[bucket][1].Add(uint64(len(sources)))
				for i := range sources {
					saveInferencePriority""")
for i, name in enumerate(("isTypeOrBaseIdenticalTo", "isTypeCloselyMatchedBy", "isTypeIdenticalTo")):
    site = f", (*Checker).{name})"
    # Restrict to the union or intersection matching call.
    line, = [line for line in s.splitlines() if "c.inferFromMatchingTypes(" in line and site in line]
    s = replace(s, line, line.replace(site, f", {i}, (*Checker).{name})"))
s = replace(s, "targets []*Type, matches func(", "targets []*Type, kind int, matches func(")
site = "var matchedSources []*Type"
s = replace(s, site, """row := &matchingWork[kind][inferenceWidth(len(sources))]
	row[0].Add(1)
	row[1].Add(uint64(len(sources))*uint64(len(targets)))
	var hits uint64
	defer func(){ row[2].Add(hits) }()
	""" + site)
s = replace(s, "if matches(c, s, t) {", "if matches(c, s, t) {\n hits++")
# Measure the candidate condition without skipping any comparisons.
candidate = subprocess.check_output(["git", "show", f"8d9a8c3:packages/tsc-go/{path}"], cwd=root, text=True)
start = candidate.index("func mayHaveCloseMatch")
end = candidate.index("func (c *Checker) isTypeCloselyMatchedBy", start)
s += "\n" + candidate[start:end]
s = replace(s, "var hits uint64", """if kind == 1 && len(sources) >= 32 && len(targets) >= 8 && !mayHaveCloseMatch(sources, targets) {
        avoided[0].Add(1); avoided[1].Add(uint64(len(sources))*uint64(len(targets)))
    }
    var hits uint64""")
s = replace(s, "inferenceWork[bucket][0].Add(1)", """if bucket == 3 {
        var counts [10]uint64
        for _, source := range sources { counts[shape(source)]++ }
        targetShape := shape(t)
        for i,count := range counts { if count != 0 { shapes[i][targetShape].Add(count) } }
    }
    inferenceWork[bucket][0].Add(1)""")
stage(path, s + """
var avoided [2]atomic.Uint64
var shapes [10][10]atomic.Uint64
func shape(t *Type) int {
    switch {
    case t.flags&TypeFlagsObject != 0: return 0
    case t.flags&TypeFlagsConditional != 0: return 1
    case t.flags&TypeFlagsTypeParameter != 0: return 2
    case t.flags&TypeFlagsIndexedAccess != 0: return 3
    case t.flags&TypeFlagsTemplateLiteral != 0: return 4
    case t.flags&TypeFlagsIntersection != 0: return 5
    case t.flags&TypeFlagsUnion != 0: return 6
    case t.flags&TypeFlagsLiteral != 0: return 7
    case t.flags&TypeFlagsPrimitive != 0: return 8
    default: return 9
    }
}
var inferenceWork [4][3]atomic.Uint64
var matchingWork [3][4][3]atomic.Uint64

func inferenceWidth(n int) int {
	switch {case n <= 1: return 0; case n < 8: return 1; case n < 32: return 2; default: return 3}
}
func InferenceWorkCounts() map[string]any {
	var direct [4][3]uint64
	var passes [3][4][3]uint64
	for i := range direct { for j := range direct[i] {
		direct[i][j] = inferenceWork[i][j].Load()
		for k := range passes { passes[k][i][j] = matchingWork[k][i][j].Load() }
	} }
	var matrix [10][10]uint64
    for i := range matrix { for j := range matrix[i] { matrix[i][j] = shapes[i][j].Load() } }
    return map[string]any{"multiple":[][4][3]uint64{direct}, "matching":passes[:], "avoided":[2]uint64{avoided[0].Load(),avoided[1].Load()}, "wideSourceTargetShapes":matrix}
}
""")
path = "cmd/tsgo/main.go"
s = replace(read(path), '"context"', '"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
stage(path, replace(s, "os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.InferenceWorkCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
