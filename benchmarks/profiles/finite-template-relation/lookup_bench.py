"""Compare the cached relation path with finite-text rejection on warmed pairs."""
import json
from pathlib import Path
import re
from statistics import median
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
go = sys.argv[2]
src = root / "internal/checker"
overlays = {}
for role in ("control", "candidate"):
    files = json.loads((out / "test-overlay.json").read_text())["Replace"]
    if role == "control":
        del files[str(src / "relater.go")]
    files[str(src / "lookup_bench_test.go")] = str(here / "lookup_bench_test.go.txt")
    cfg = out / (role + "-benchmark.json")
    cfg.write_text(json.dumps({"Replace": files}))
    binary = out / (role + "-lookup.test")
    subprocess.run([go, "test", "-c", "-overlay=" + str(cfg), "-o", binary, "./internal/checker"], cwd=root, check=True)
    overlays[role] = binary
report = {"samples": []}
for role in ("control", "candidate", "candidate", "control", "control", "candidate"):
    command = [overlays[role], "-test.run=^$", "-test.bench=^BenchmarkWarmFiniteTemplateMismatch$", "-test.benchtime=1s", "-test.cpu=1"]
    txt = subprocess.check_output(command, cwd=root, text=True)
    ns, size, allocs = re.findall(r"\s([\d.]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op", txt)[0]
    report["samples"].append(dict(role=role, nsPerOp=float(ns), bytesPerOp=int(size), allocsPerOp=int(allocs)))
for role in overlays:
    report[role + "MedianNs"] = median(r["nsPerOp"] for r in report["samples"] if r["role"] == role)
(here / "lookup.json").write_text(json.dumps(report, indent=2) + "\n")
print(report)
