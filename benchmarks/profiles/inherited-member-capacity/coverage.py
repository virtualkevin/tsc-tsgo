"""Compare each active capacity hint to the final distinct name count."""
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
config = json.loads((out / "overlay.json").read_text())
source = (out / "pending_members.go").read_text()
site = "members := p.ownTable()"
assert source.count(site) == 1
source = source.replace(site, """ownCount := len(p.source.entries)
    hint := ownCount
    if previous := p.source.lastMemberNames; previous != nil && p.hasBases && !p.resolving {
        hint = max(ownCount, min(4096, len(previous.names)))
    }
    members := p.ownTable()""")
site = "t.members = members\n\tif p.hasBases"
assert source.count(site) == 1
source = source.replace(site, """if hint > ownCount {
        row := 1
        if hint < len(members) { row = 0 } else if hint > len(members) { row = 2 }
        hist := &capacityHistogram[row]
        hist[0].Add(1)
        hist[1].Add(uint64(ownCount))
        hist[2].Add(uint64(hint))
        hist[3].Add(uint64(len(members)))
    }
    t.members = members
    if p.hasBases""")
source = source.replace('import (', 'import (\n"sync/atomic"', 1)
source += """
var capacityHistogram [3][4]atomic.Uint64
func MemberCapacityHistogram() [3][4]uint64 {
    var out [3][4]uint64
    for i := range out { for j := range out[i] {out[i][j] = capacityHistogram[i][j].Load()} }
    return out
}
"""
observed = out / "observed_pending.go"
observed.write_text(source)
config["Replace"][str(root / "internal/checker/pending_members.go")] = str(observed)
main = root / "cmd/tsgo/main.go"
source = main.read_text()
assert source.count("os.Exit(runMain())") == 1
source = source.replace('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
source = source.replace("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.MemberCapacityHistogram()); os.Exit(status)")
observed = out / "observed_main.go"
observed.write_text(source)
config["Replace"][str(main)] = str(observed)
overlay = out / "coverage-overlay.json"
overlay.write_text(json.dumps(config))
binary = out / "observed"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(overlay), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
          "rows": ["underestimate", "exact", "overestimate"],
          "columns": ["materializations", "originalOwnCapacity", "hintedCapacity", "finalDistinctNames"],
          "projects": {}}
for project, commit, counts in observed_projects(binary):
    assert len(counts) == 3 and all(len(row) == 4 for row in counts)
    for index, (n, own, hint, final) in enumerate(counts):
        assert hint >= own + n
        assert (hint <= final - n if index == 0 else hint >= final + n if index == 2 else hint == final)
    report["projects"][project] = {"commit": commit, "counts": counts}
    print(project, counts, flush=True)
(here / "coverage.json").write_text(json.dumps(report, indent=2) + "\n")
