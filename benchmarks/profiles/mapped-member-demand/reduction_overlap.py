"""Measure the outcomes of skipped-side lookups during intersection reduction."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

repo = here.parents[2]
root = repo / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = {}


def edit(file, changes):
    source = subprocess.check_output(
        ["git", "show", "bd1baea:packages/tsc-go/" + file], cwd=repo, text=True
    )
    for old, new in changes:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    dest = out / Path(file).name
    dest.write_text(source)
    overlay[str(root / file)] = str(dest)


edit("internal/checker/lazy_properties.go", [
    ('"slices"', '"slices"\n "sync/atomic"'),
    ('// Ports tsc-ts 0d434', '''
// Classify all visited names by whether the enumerated group contains a mapped symbol.
var reductionLookup [2][6]atomic.Uint64

func ReductionLookupCounts() [2][6]uint64 {
    var out [2][6]uint64
    for i := range out {
        for j := range out[i] {out[i][j] = reductionLookup[i][j].Load()}
    }
    return out
}

// Ports tsc-ts 0d434'''),
    ('props := byName[name]\n', '''props := byName[name]
        cohort := 0
        for _, prop := range props {
            if prop.CheckFlags & ast.CheckFlagsMapped != 0 {cohort = 1; break}
        }
        outcome := 0
'''),
    ('if prop != nil && !slices.Contains(props, prop) {', '''switch {
            case prop == nil: outcome = 1
            case slices.Contains(props,prop): outcome = 2
            default: outcome = 3
            }
            if prop != nil && !slices.Contains(props, prop) {'''),
    ('if len(props) < 2 ||', '''reductionLookup[cohort][outcome].Add(1)
        if outcome == 1 && len(props) == 1 {reductionLookup[cohort][4].Add(1)}
        if len(props) < 2 ||'''),
    ('combined := c.getPropertyOfUnionOrIntersectionType(t, name, true)', '''reductionLookup[cohort][5].Add(1)
        combined := c.getPropertyOfUnionOrIntersectionType(t, name, true)''')
])
edit("cmd/tsgo/main.go", [
    ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ('os.Exit(runMain())', 'status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.ReductionLookupCounts()); os.Exit(status)')
])
config = out / "overlay.json"
config.write_text(json.dumps({"Replace": overlay}))
binary = out / "tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(config),
                "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {
    "binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "rows": ["no enumerated mapped symbol", "contains enumerated mapped symbol"],
    "columns": ["no skipped side", "miss", "same symbol", "distinct symbol",
                "singleton on miss (subset of miss)", "requested combined symbol (all outcomes)"],
    "projects": {}
}
for name, commit, counts in observed_projects(binary):
    assert len(counts) == 2 and all(len(row) == 6 and row[4] <= row[1] for row in counts)
    report["projects"][name] = {"commit": commit, "counts": counts}
    print(name, counts, flush=True)
(here / "reduction-overlap.json").write_text(json.dumps(report, indent=2) + "\n")
