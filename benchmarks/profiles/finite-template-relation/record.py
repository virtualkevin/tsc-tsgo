"""Record matched Sentry timings after checking the complete input manifests."""
import gzip
import hashlib
import json
from pathlib import Path
from statistics import median
import sys

here = Path(__file__).resolve().parent
ref = json.loads(gzip.decompress((here.parent / "inherited-member-capacity/screen.json.gz").read_bytes()))
old = next(p for p in ref["projects"] if p["name"] == "sentry")
data = Path(sys.argv[1]).read_bytes()
run = json.loads(data)
assert run["status"] == "passed" and run["warmups"] == 0 and run["runs"] == 4
assert run["binaries"]["baseline"]["sha256"] == ref["binaries"]["baseline"]["sha256"]
assert run["environment"]["compilerEnvironment"] == ref["environment"]["compilerEnvironment"]
assert run["binaries"]["candidate"]["sha256"] == hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()
project, = run["projects"]
for key in ("name", "commit", "compilerArgs", "diagnosticCount", "status"):
    assert project[key] == old[key]
assert project["resourceWrapperVerifiedAfter"] and project["status"] == "passed" and project["diagnosticCount"] == 0
for side in ("baseline", "candidate"):
    assert project["preflight"][side]["inputs"] == old["preflight"][side]["inputs"]
pairs = project["pairs"]
assert [r["order"] for r in pairs] == [["baseline","candidate"],["candidate","baseline"]] * 2
a, b = (median(r[role] for r in pairs) for role in ("baseline", "candidate"))
wins = sum(r["baseline"] > r["candidate"] for r in pairs)
row = f"| Reject finite-string template mismatches at relation entry | Sentry | Matched ordinary Go build | {a:.2f} | {b:.2f} | {a/b:.3f}× | 4 | Candidate faster in {wins}/4 pairs. [Samples](benchmarks/profiles/finite-template-relation/sentry.json.gz) |"
table = here.parents[2] / "PERF.md"
assert row not in table.read_text()
(here / "sentry.json.gz").write_bytes(gzip.compress(data, mtime=0))
with table.open("a") as f:
    f.write(row + "\n")
print(row)
