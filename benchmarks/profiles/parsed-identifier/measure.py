"""Compare two parser test binaries on the pinned source corpus."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess

here = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("control", type=Path)
parser.add_argument("candidate", type=Path)
args = parser.parse_args()
binaries = {"control": args.control.resolve(), "candidate": args.candidate.resolve()}
env = dict(os.environ, IDENTIFIER_ROOT=str(here.parents[2]/"upstream/benchmarks"),
           IDENTIFIER_INPUTS=str(here/"inputs.json"))
def run(engine, *flags):
    return subprocess.check_output([binaries[engine], *flags], env=env, text=True, timeout=240)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
trees = {}
for engine in binaries:
    trees[engine] = [s for s in run(engine,"-test.run=^TestIdentifierTreeFingerprint$","-test.v").splitlines() if s.startswith("TREE ")]
assert len(trees["control"]) == 67 and trees["control"] == trees["candidate"]
(here/"trees.txt.gz").write_bytes(gzip.compress(("\n".join(trees["control"])+"\n").encode(),mtime=0))

pattern = re.compile(r"^BenchmarkIdentifierProjectParsing/(\w+)-\d+\s+(\d+)\s+([\d.]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op$", re.M)
projects = {"sentry","trpc","vscode","typeorm"}
rows = []
flags = ["-test.run=^$", "-test.bench=^BenchmarkIdentifierProjectParsing$", "-test.benchtime=300ms"]
for trial in range(6):
    for engine in (list(binaries) if trial%2==0 else reversed(binaries)):
        values = pattern.findall(run(engine,*flags))
        assert {v[0] for v in values} == projects and len(values)==4
        for p,n,ns,b,a in values:
            rows.append(dict(project=p, engine=engine, trial=trial, iterations=int(n), ns=float(ns), bytes=int(b), allocations=int(a)))
report = dict(inputsSha256=digest(here/"inputs.json"), executables={e:digest(p) for e,p in binaries.items()},
              trees=len(trees["control"]), flags=flags, samples=rows, medians={})
for project in sorted(projects):
    report["medians"][project] = {e:statistics.median(r["ns"] for r in rows if r["project"]==project and r["engine"]==e) for e in binaries}
print(report["medians"],flush=True)
(here/"parser.json").write_text(json.dumps(report,indent=2)+"\n")
