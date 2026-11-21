"""Verify paired Go project measurements before recording them in PERF.md."""
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys

here = Path(__file__).resolve().parent
data = Path(sys.argv[1]).read_bytes()
report = json.loads(data)
ref = json.loads(gzip.decompress((here.parent / "mapped-member-demand/screen.json.gz").read_bytes()))
frozen = {p["name"]: p for p in ref["projects"]}
assert report["status"] == "passed" and report["runs"] == 2 and report["warmups"] == 0
assert report["binaries"]["baseline"]["sha256"] == ref["binaries"]["baseline"]["sha256"]
assert report["binaries"]["candidate"]["sha256"] == hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()
assert {p["name"] for p in report["projects"]} == {"sentry", "trpc", "typeorm", "vscode"}
rows = []
for project in report["projects"]:
    name = project["name"]
    assert project["status"] == "passed" and project["diagnosticCount"] == 0
    assert project["resourceWrapperVerifiedAfter"]
    assert project["commit"] == frozen[name]["commit"] and project["compilerArgs"] == frozen[name]["compilerArgs"]
    for side in ("candidate", "baseline"):
        assert project["preflight"][side]["inputs"] == frozen[name]["preflight"]["baseline"]["inputs"]
    pairs = project["pairs"]
    assert [p["order"] for p in pairs] == [["baseline", "candidate"], ["candidate", "baseline"]]
    old, new = (statistics.median(p[k] for p in pairs) for k in ("baseline", "candidate"))
    wins = sum(p["candidate"] < p["baseline"] for p in pairs)
    rows.append(f"| Ordered two-part intersection | {name} | Matched ordinary Go build | {old:.2f} | {new:.2f} | {old/new:.3f}× | 2 | Candidate faster in {wins}/2 pairs. [Samples](benchmarks/profiles/ordered-intersection-pair/screen.json.gz) |")
table = here.parents[2] / "PERF.md"
assert all(row not in table.read_text() for row in rows)
(here / "screen.json.gz").write_bytes(gzip.compress(data, mtime=0))
with table.open("a") as f:
    f.write("\n".join(rows) + "\n")
print(*rows, sep="\n")
