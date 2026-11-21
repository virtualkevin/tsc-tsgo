"""Verify timed binaries, flags and file contents against the frozen Sentry control."""
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
data = Path(sys.argv[1]).read_bytes()
report = json.loads(data)
reference = json.loads(gzip.decompress((here.parent/"jsx-absent-discriminants/groups-watched.json.gz").read_bytes()))
assert report["status"] == "passed" and report["warmups"] == 0 and report["runs"] == 2
assert report["binaries"]["baseline"]["sha256"] == reference["binaries"]["baseline"]["sha256"]
assert report["binaries"]["candidate"]["sha256"] == hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()
p, = report["projects"]
ref = next(x for x in reference["projects"] if x["name"]=="sentry")
assert p["name"]=="sentry" and p["commit"]==ref["commit"] and p["compilerArgs"]==ref["compilerArgs"]
assert p["status"]=="passed" and p["resourceWrapperVerifiedAfter"] and p["diagnosticCount"]==0
for key in ("baseline","candidate"):
    assert p["preflight"][key]["inputs"] == ref["preflight"]["baseline"]["inputs"]
assert [r["order"] for r in p["pairs"]] == [["baseline","candidate"],["candidate","baseline"]]
a,b = (statistics.median(r[k] for r in p["pairs"]) for k in ("baseline","candidate"))
wins=sum(r["candidate"]<r["baseline"] for r in p["pairs"])
row=f"| Reuse completed JSX absence filters | Sentry | Matched ordinary Go build | {a:.2f} | {b:.2f} | {a/b:.3f}× | 2 | Candidate faster in {wins}/2 pairs. [Samples](benchmarks/profiles/jsx-member-filter/sentry.json.gz) |"
assert row not in (root/"PERF.md").read_text()
(here/"sentry.json.gz").write_bytes(gzip.compress(data,mtime=0))
with (root/"PERF.md").open("a") as f: f.write(row+"\n")
print(row)
