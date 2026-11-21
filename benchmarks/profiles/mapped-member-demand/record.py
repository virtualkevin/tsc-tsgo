"""Add the measured mapped-key screen after checking the matched Go inputs."""
import gzip
import json
from pathlib import Path
import statistics
import sys

here=Path(__file__).resolve().parent
data=Path(sys.argv[1]).read_bytes()
screen=json.loads(data)
parity=json.loads((here/"key-parity.json").read_bytes())
assert screen["status"]=="passed"
if (screen["runs"],screen["warmups"])==(2,0):
    ordinary,experimental="baseline","candidate"
    archive="screen"
    projects={"vscode","sentry","typeorm","trpc"}
else:
    assert (screen["runs"],screen["warmups"])==(8,1)
    ordinary,experimental="candidate","baseline"
    archive="reversed-small"
    projects={"typeorm","trpc"}
assert screen["binaries"][ordinary]["sha256"]==parity["binaries"]["ordinary"]
assert screen["binaries"][experimental]["sha256"]==parity["binaries"]["candidate"]
runs=screen["runs"]
previous=json.loads(gzip.decompress((here.parent/"union-property-construction/screen.json.gz").read_bytes()))
refs={p["name"]:p for p in previous["projects"]}
assert len(screen["projects"])==len(projects) and {p["name"] for p in screen["projects"]}==projects
rows=[]
for p in screen["projects"]:
    name=p["name"]
    ref=refs[name]
    assert p["commit"]==ref["commit"] and p["compilerArgs"]==ref["compilerArgs"]
    assert p["status"]=="passed" and p["diagnosticCount"]==0 and p["resourceWrapperVerifiedAfter"]
    for side in ("baseline","candidate"):
        assert p["preflight"][side]["inputs"]==ref["preflight"]["baseline"]["inputs"]
    pairs=p["pairs"]
    assert [r["order"] for r in pairs]==[["baseline","candidate"],["candidate","baseline"]]*(runs//2)
    a,b=(statistics.median(r[k] for r in pairs) for k in (ordinary,experimental))
    wins=sum(r[experimental]<r[ordinary] for r in pairs)
    rows.append(f"| Reuse identical mapped key and name links | {name} | Matched ordinary Go build | {a:.2f} | {b:.2f} | {a/b:.3f}× | {runs} | Candidate faster in {wins}/{runs} pairs. [Samples](benchmarks/profiles/mapped-member-demand/{archive}.json.gz) |")
table=here.parents[2]/"PERF.md"
assert all(row not in table.read_text() for row in rows)
(here/f"{archive}.json.gz").write_bytes(gzip.compress(data,mtime=0))
with table.open("a") as f:
    f.write("\n".join(rows)+"\n")
print(*rows,sep="\n")
