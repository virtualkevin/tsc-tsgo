"""Read cumulative Go allocation counters once, after a complete CLI invocation."""
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
main = root / "cmd/tsgo/main.go"
source = main.read_text()
assert source.count("os.Exit(runMain())") == 1
source = source.replace('"context"', '"context"\n "runtime"\n "encoding/json"').replace("os.Exit(runMain())", """status := runMain()
    var stats runtime.MemStats
    runtime.ReadMemStats(&stats)
    json.NewEncoder(os.Stderr).Encode(struct {
        TotalAlloc uint64
        Mallocs uint64
        NumGC uint32
    }{stats.TotalAlloc, stats.Mallocs, stats.NumGC})
    os.Exit(status)""")
observed = out / "allocation_main.go"
observed.write_text(source)
binaries = {}
for role in ("control", "candidate"):
    paths = dict(config["Replace"]) if role == "candidate" else {}
    paths[str(main)] = str(observed)
    overlay = out / (role + "-total.json")
    overlay.write_text(json.dumps({"Replace": paths}))
    binary = out / (role + "-total")
    subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(overlay), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
    binaries[role] = binary
report = {"binaries": {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in binaries.items()}, "projects": {}}
for project in ("sentry", "trpc", "typeorm", "vscode"):
    runs = []
    for role in ("control", "candidate", "candidate", "control"):
        (name, commit, counts), = observed_projects(binaries[role], projects={project})
        assert name == project and counts["TotalAlloc"] > 0 and counts["Mallocs"] > 0
        runs.append({"role": role, **counts})
        print(name, role, counts, flush=True)
    report["projects"][project] = {"commit": commit, "runs": runs}
    (out / "total-alloc-partial.json").write_text(json.dumps(report, indent=2) + "\n")
(here / "total-alloc.json").write_text(json.dumps(report, indent=2) + "\n")
