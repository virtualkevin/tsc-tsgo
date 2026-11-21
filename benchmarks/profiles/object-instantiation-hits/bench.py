"""Time warmed object-instantiation lookups and count allocations with Go's benchmark harness."""
from pathlib import Path
import hashlib
import json
import re
import statistics
import subprocess
import sys

here = Path(__file__).resolve().parent
bins = dict(zip(("control","candidate"),(Path(x).resolve() for x in sys.argv[1:]),strict=True))
report = {"sha256":{k:hashlib.sha256(b.read_bytes()).hexdigest() for k,b in bins.items()},
          "iterations":40000, "pairs":[]}
for i in range(6):
    pair = {}
    for name in (bins if i % 2==0 else reversed(bins)):
        out = subprocess.check_output([bins[name],"-test.run=^TestObjectMissRetainsArgumentAndAlias$",
                                       "-test.bench=^BenchmarkObjectInstantiationHit$","-test.benchtime=40000x",
                                       "-test.benchmem","-test.cpu=1"],text=True)
        assert out.rstrip().endswith("PASS")
        rows = {}
        for n,ns,b,a in re.findall(r"BenchmarkObjectInstantiationHit/(\d+)(?:-\d+)?\s+40000\s+([\d.]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op",out):
            rows[n] = {"ns":float(ns),"bytes":int(b),"allocs":int(a)}
        assert len(rows)==4, out
        pair[name] = rows
    report["pairs"].append(pair)
(here/"bench.json").write_text(json.dumps(report,indent=2)+"\n")
for n in ("1","2","4","5"):
    print(n, {k:[statistics.median(p[k][n][col] for p in report["pairs"]) for col in ("ns","bytes","allocs")] for k in bins})
