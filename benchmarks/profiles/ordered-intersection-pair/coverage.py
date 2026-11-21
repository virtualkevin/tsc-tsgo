"""Count actual optimized intersections with the same overlay and frozen projects."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
overlay = json.loads((out / "overlay.json").read_text())
path = out / "lazy_properties.go"
source = path.read_text().replace('"slices"', '"slices"\n "sync/atomic"')
layout = len(sys.argv) > 3 and sys.argv[3] == "layout"
if layout:
    assert source.count("seen := make(map[string]struct{}, len(properties))") == 1
    assert source.count("return false, false") == 1
    assert source.count("symbols := slices.Clone(properties)") == 1
    source = source.replace("seen := make(map[string]struct{}, len(properties))",
                            "rebuiltPairs.Add(1); rebuiltNames.Add(uint64(len(properties)))\n seen := make(map[string]struct{}, len(properties))")
    source = source.replace("return false, false", "rejectedPairs.Add(1); rejectedNames.Add(uint64(len(properties))); return false, false")
    source = source.replace("symbols := slices.Clone(properties)",
                            "acceptedPairs.Add(1); acceptedNames.Add(uint64(len(properties))); symbols := slices.Clone(properties)")
else:
    source = source.replace("type entry struct {", """acceptedPairs.Add(1)
        acceptedNames.Add(uint64(len(properties)))
        type entry struct {""")
    source = source.replace("if properties[i-1].Name >= properties[i].Name {", """if properties[i-1].Name >= properties[i].Name {
            rejectedPairs.Add(1)
            rejectedNames.Add(uint64(len(properties)))""")
source += """
var acceptedPairs, acceptedNames, rejectedPairs, rejectedNames, rebuiltPairs, rebuiltNames atomic.Uint64
func OrderedPairCounts() []uint64 {
    return []uint64{acceptedPairs.Load(), acceptedNames.Load(), rejectedPairs.Load(), rejectedNames.Load(), rebuiltPairs.Load(), rebuiltNames.Load()}
}
"""
observed = out / "observed.go"
observed.write_text(source)
overlay["Replace"][str(root / "internal/checker/lazy_properties.go")] = str(observed)
main = root / "cmd/tsgo/main.go"
source = main.read_text().replace('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
source = source.replace("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.OrderedPairCounts()); os.Exit(status)")
observed_main = out / "observed_main.go"
observed_main.write_text(source)
overlay["Replace"][str(main)] = str(observed_main)
config = out / "coverage-overlay.json"
config.write_text(json.dumps(overlay))
binary = out / "observed"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(config), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
          "columns": ["acceptedPairs", "acceptedNames", "unorderedPairs", "unorderedNames"], "projects": {}}
for name, commit, counts in observed_projects(binary):
    assert len(counts) == 6 and counts[1] >= 9 * counts[0] and counts[3] >= 9 * counts[2]
    if layout:
        report["columns"] = ["acceptedPairs", "acceptedNames", "duplicatePairs", "duplicateNames", "planMissesIncludingDuplicates", "namesOnPlanMisses"]
        assert counts[2] <= counts[4] <= counts[0] + counts[2]
    else:
        assert counts[4:] == [0, 0]
        counts = counts[:4]
    report["projects"][name] = {"commit": commit, "counts": counts}
    print(name, counts, flush=True)
(here / ("layout-coverage.json" if layout else "coverage.json")).write_text(json.dumps(report, indent=2) + "\n")
