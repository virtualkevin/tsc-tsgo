"""Verify and record the paired ablations using hashes from the previous full screen."""
from pathlib import Path
import gzip
import hashlib
import json
import statistics
import sys

here = Path(__file__).resolve().parent
repo = here.parents[2]
original = json.loads(gzip.decompress((here/"groups-watched.json.gz").read_bytes()))
source = Path(sys.argv[1])
write_binary = Path(sys.argv[2])
write_hash = hashlib.sha256(write_binary.read_bytes()).hexdigest()
raw = source.read_bytes()
report = json.loads(raw)
ids = tuple(report["binaries"][k]["sha256"] for k in ("baseline","candidate"))
if ids == (original["binaries"]["baseline"]["sha256"],write_hash):
    stage, baseline, archive = "Resolved symbol write guards alone", "Matched ordinary Go build", "write-guards"
elif ids == (write_hash,original["binaries"]["candidate"]["sha256"]):
    stage, baseline, archive = "Add grouped JSX reuse to write guards", "Write guards alone", "add-reuse"
else:
    raise ValueError("Unrecognized binary pair")
projects = {p["name"] for p in report["projects"]}
if projects == {"sentry","vscode"}:
    runs, warmups = 2, 0
    archive += "-large"
else:
    assert projects == {"typeorm","trpc"}
    runs, warmups = 8, 1
assert report["status"] == "passed" and report["runs"]==runs and report["warmups"]==warmups
rows=[]
for project in report["projects"]:
    ref=next(p for p in original["projects"] if p["name"]==project["name"])
    assert project["status"]=="passed" and project["resourceWrapperVerifiedAfter"] and project["diagnosticCount"]==0
    assert project["commit"]==ref["commit"] and project["compilerArgs"]==ref["compilerArgs"]
    assert project["preflight"]["baseline"]["inputs"]==project["preflight"]["candidate"]["inputs"]==ref["preflight"]["baseline"]["inputs"]
    pairs=project["pairs"]
    assert [p["order"] for p in pairs]==[["baseline","candidate"],["candidate","baseline"]]*(runs//2)
    a,b=(statistics.median(pair[k] for pair in pairs) for k in ("baseline","candidate"))
    wins=sum(pair["candidate"]<pair["baseline"] for pair in pairs)
    interference = " Offline profile analysis overlapped this screen." if archive == "write-guards-large" else ""
    rows.append(f"| {stage} | {project['name']} | {baseline} | {a:.2f} | {b:.2f} | {a/b:.3f}× | {runs} | Candidate faster in {wins}/{runs} pairs.{interference} [Samples](benchmarks/profiles/jsx-absent-discriminants/{archive}.json.gz) |")
assert rows and not any(row in (repo/"PERF.md").read_text() for row in rows)
(here/f"{archive}.json.gz").write_bytes(gzip.compress(raw,mtime=0))
with (repo/"PERF.md").open("a") as f:
    f.write("\n".join(rows)+"\n")
print(*rows,sep="\n")
