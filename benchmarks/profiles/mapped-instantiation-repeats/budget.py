"""Partition each mapped-symbol stack by its outermost resolver source line."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
archive = here.parent/"avx-opportunity-audit"
source = subprocess.check_output(
    ["git", "show", "395df1a:packages/tsc-go/internal/checker/checker.go"],
    cwd=here.parents[2], text=True,
).splitlines()
assert "getTypeOfMappedSymbol(symbol" in source[20880]
assert "c.instantiateType(templateType, mapper)" in source[20890]

def analyze(raw):
    samples,locations = raw.split("Locations\n",1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        m = re.match(r"^\s*(\d+):\s+0x[\da-f]+",line)
        if m:
            addr=int(m[1])
            frames[addr]=[]
        frame=re.search(r"/checker\.\(\*Checker\)\.getTypeOfMappedSymbol\s+\S+/checker/checker.go:(\d+):",line)
        if frame:
            frames[addr].append(int(frame[1]))
    counts=Counter()
    total=0
    for line in samples.splitlines():
        m=re.match(r"^\s+\d+\s+(\d+):\s*(.*)$",line)
        if m:
            ns=int(m[1]); total+=ns
            calls=[n for a in map(int,m[2].split()) for n in frames[a]]
            if calls:
                counts[calls[-1]]+=ns
    assert counts and all(20881<=n<=20912 for n in counts)
    return dict(totalCpuNs=total,outermostMappedCpuNs=sum(counts.values()),
                lines=[dict(line=n,source=source[n-1].strip(),cpuNs=v) for n,v in sorted(counts.items())])
report={}
for row in json.loads((archive/"report.json").read_text())["projects"]:
    raw=gzip.decompress((archive/(row["workload"]+".raw.gz")).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==row["rawSha256"]
    report[row["workload"]]=analyze(raw.decode())
    assert report[row["workload"]]["totalCpuNs"]==row["totalCpuNs"]
profile=here.parent/"grouped-pointer-probes/advised-cpu.pb.gz"
binary=here.parents[2]/"packages/tsc-go/dist/tsc-go-large-heap-pages"
report["sentry-size-aware"]=analyze(subprocess.check_output([sys.argv[1],"-raw",binary,profile],text=True))
(here/"cpu.json").write_text(json.dumps(report,indent=2)+"\n")
