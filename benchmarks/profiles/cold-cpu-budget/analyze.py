"""Compare measured per-process CPU work with idealized 10x wall-time budgets."""
from pathlib import Path
import hashlib
import json
from statistics import median

here = Path(__file__).resolve().parent
source = here.parent/"large-heap-page-advice/three-way.json"
run = json.loads(source.read_text())
assert run["status"]=="passed"
report = {"samplesSha256":hashlib.sha256(source.read_bytes()).hexdigest(),"projects":{}}
for name,p in run["projects"].items():
    measured = [r for r in p["rows"] if r["block"]>0]
    def rows(mode):
        return [r for r in measured if r["mode"]==mode]
    wall = median(r["ms"] for r in rows("native"))/1000
    assert wall==p["medians"]["native"]["ms"]/1000
    target = wall/10
    go = rows("advised")
    cpu = median(r["userSeconds"]+r["systemSeconds"] for r in go)
    native_cpu = median(r["userSeconds"]+r["systemSeconds"] for r in rows("native"))
    report["projects"][name] = dict(nativeWallSeconds=wall, goalWallSeconds=target,
        goCpuSeconds=cpu,nativeCpuSeconds=native_cpu,
        observedGoCores=median((r["userSeconds"]+r["systemSeconds"])/(r["ms"]/1000) for r in go),
        idealCoresForUnchangedWork=cpu/target,
        cpuReductionNeededAtFiveCores=cpu/(target*5),
        cpuReductionNeededAtEightCores=cpu/(target*8))
(here/"results.json").write_text(json.dumps(report,indent=2)+"\n")
