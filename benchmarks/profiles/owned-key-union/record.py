"""Verify full-check inputs, compiler binaries and pairing before archiving results."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
data = Path(sys.argv[1]).read_bytes()
run = json.loads(data)
prior = json.loads(gzip.decompress((here.parent / "inherited-member-capacity/screen.json.gz").read_bytes()))
assert run["status"] == "passed" and run["runs"] == 2 and run["warmups"] == 0
assert run["binaries"]["candidate"]["sha256"] == hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()
assert run["binaries"]["baseline"]["sha256"] == prior["binaries"]["baseline"]["sha256"]
assert run["environment"]["compilerEnvironment"] == prior["environment"]["compilerEnvironment"]
rows = []
for p, ref in zip(run["projects"], prior["projects"], strict=True):
    for k in ("name", "commit", "compilerArgs", "diagnosticCount", "status"):
        assert p[k] == ref[k]
    assert p["resourceWrapperVerifiedAfter"] and p["diagnosticCount"] == 0 and p["status"] == "passed"
    for side in ("baseline", "candidate"):
        assert p["preflight"][side]["inputs"] == ref["preflight"][side]["inputs"]
    assert [r["order"] for r in p["pairs"]] == [["baseline","candidate"],["candidate","baseline"]]
    wins = sum(r["candidate"] < r["baseline"] for r in p["pairs"])
    a, b = (p[side]["medianMs"] for side in ("baseline","candidate"))
    rows.append(f"| Construct complete literal key union in owned storage | {p['name']} | Matched ordinary Go build | {a:.2f} | {b:.2f} | {a/b:.3f}× | 2 | Candidate faster in {wins}/2 pairs. [Samples](benchmarks/profiles/owned-key-union/screen.json.gz) |")
table = here.parents[2] / "PERF.md"
assert len(rows) == 4 and all(row not in table.read_text() for row in rows)
(here / "screen.json.gz").write_bytes(gzip.compress(data, mtime=0))
with table.open("a") as f:
    f.write("\n".join(rows) + "\n")
print(*rows, sep="\n")
