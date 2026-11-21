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
source = source.replace("type entry struct {", """acceptedPairs.Add(1)
    acceptedNames.Add(uint64(len(properties)))
    type entry struct {""")
source = source.replace("if properties[i-1].Name >= properties[i].Name {", """if properties[i-1].Name >= properties[i].Name {
        rejectedPairs.Add(1)
        rejectedNames.Add(uint64(len(properties)))""")
source += """
var acceptedPairs, acceptedNames, rejectedPairs, rejectedNames atomic.Uint64
func OrderedPairCounts() [4]uint64 {
    return [4]uint64{acceptedPairs.Load(), acceptedNames.Load(), rejectedPairs.Load(), rejectedNames.Load()}
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
    assert len(counts) == 4 and counts[1] >= 9 * counts[0] and counts[3] >= 9 * counts[2]
    report["projects"][name] = {"commit": commit, "counts": counts}
    print(name, counts, flush=True)
(here / "coverage.json").write_text(json.dumps(report, indent=2) + "\n")
