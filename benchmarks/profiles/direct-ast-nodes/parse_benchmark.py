"""Alternate prebuilt Go parser test binaries on a fixed batch of named imports."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys

control, candidate, output = map(Path, sys.argv[1:])
bins = {"control": control.resolve(), "candidate": candidate.resolve()}
args = ["-test.run=^$", "-test.bench=^BenchmarkImportPairParse$", "-test.benchtime=15x", "-test.count=1"]
report = {"binarySha256": {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in bins.items()},
          "imports": 1000, "args": args, "excludedWarmups": 1, "blocks": []}
for index in range(-1, 6):
    order = ("control", "candidate") if index % 2 == 0 else ("candidate", "control")
    block = {}
    for role in order:
        log = subprocess.check_output([bins[role], *args], text=True)
        m = re.search(r"^BenchmarkImportPairParse-\d+\s+15\s+(\d+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op$", log, re.M)
        assert m, log
        block[role] = dict(zip(("ns", "bytes", "allocations"), map(int, m.groups()), strict=True))
    if index >= 0:
        report["blocks"].append(block)
report["median"] = {r: {unit: statistics.median(x[r][unit] for x in report["blocks"])
                        for unit in ("ns", "bytes", "allocations")} for r in bins}
output.write_text(json.dumps(report, indent=2) + "\n")
print(report["median"])
