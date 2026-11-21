"""Check identities, same-work invariants and paired execution before recording times."""
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]
data=Path(sys.argv[1]).read_bytes()
report=json.loads(data)
ref=json.loads(gzip.decompress((here.parent/"jsx-absent-discriminants/groups-watched.json.gz").read_bytes()))
assert report["status"]=="passed"
assert report["binaries"]["baseline"]["sha256"]==ref["binaries"]["baseline"]["sha256"]
assert report["binaries"]["candidate"]["sha256"]==hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()
expected={p["name"]:p for p in ref["projects"]}
projects={p["name"] for p in report["projects"]}
if projects == set(expected):
    runs,warmups,archive = 2,0,"screen"
else:
    assert projects == {"trpc","typeorm"}
    runs,warmups,archive = 8,1,"small-repeat"
assert len(projects)==len(report["projects"]) and (report["runs"],report["warmups"])==(runs,warmups)
rows=[]
for p in report["projects"]:
    name=p["name"]
    old=expected[name]
    assert p["status"]=="passed" and p["commit"]==old["commit"] and p["compilerArgs"]==old["compilerArgs"]
    assert p["resourceWrapperVerifiedAfter"] and p["diagnosticCount"]==0
    for side in ("baseline","candidate"): assert p["preflight"][side]["inputs"]==old["preflight"]["baseline"]["inputs"]
    pairs=p["pairs"]
    assert [r["order"] for r in pairs]==[["baseline","candidate"],["candidate","baseline"]]*(runs//2)
    a,b=(statistics.median(r[k] for r in pairs) for k in ("baseline","candidate"))
    wins=sum(r["candidate"]<r["baseline"] for r in pairs)
    rows.append(f"| Skip apparent-type reduction for plain objects | {name} | Matched ordinary Go build | {a:.2f} | {b:.2f} | {a/b:.3f}× | {runs} | Candidate faster in {wins}/{runs} pairs. [Samples](benchmarks/profiles/union-property-construction/{archive}.json.gz) |")
assert all(row not in (root/"PERF.md").read_text() for row in rows)
(here/f"{archive}.json.gz").write_bytes(gzip.compress(data,mtime=0))
with (root/"PERF.md").open("a") as f: f.write("\n".join(rows)+"\n")
print(*rows,sep="\n")
