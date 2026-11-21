"""Record a paired result against either public 0.0.2 or the matched Go build."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
data = Path(sys.argv[1]).read_bytes()
j = json.loads(data)
public = sys.argv[2] == "public"
assert public or sys.argv[2] == "go"
ref_name = "ordered-intersection-pair/layout-public.json.gz" if public else "inherited-member-capacity/screen.json.gz"
ref = json.loads(gzip.decompress((here.parent / ref_name).read_bytes()))
old = {p["name"]:p for p in ref["projects"]}
assert j["status"] == "passed" and j["runs"] == 2 and j["warmups"] == 0
assert j["environment"]["compilerEnvironment"] == ref["environment"]["compilerEnvironment"]
assert j["binaries"]["baseline"]["sha256"] == ref["binaries"]["baseline"]["sha256"]
assert j["binaries"]["candidate"]["sha256"] == json.loads((here/"validation.json").read_text())["candidateSha256"]
assert {p["name"] for p in j["projects"]} == (old.keys() if public else {"sentry"})
label = "Public npm tsc-ts@0.0.2" if public else "Matched ordinary Go build"
archive = "public.json.gz" if public else "sentry.json.gz"
rows = []
for p in j["projects"]:
    r = old[p["name"]]
    assert p["commit"] == r["commit"] and p["compilerArgs"] == r["compilerArgs"]
    assert p["resourceWrapperVerifiedAfter"] and p["status"] == "passed" and p["diagnosticCount"] == 0
    for role in ("candidate","baseline"):
        assert p["preflight"][role]["inputs"] == r["preflight"][role]["inputs"]
    assert [t["order"] for t in p["pairs"]] == [["baseline","candidate"],["candidate","baseline"]]
    a,b = (p[role]["medianMs"] for role in ("baseline","candidate"))
    wins = sum(t["baseline"] > t["candidate"] for t in p["pairs"])
    rows.append(f"| Skip redundant named union coverage search | {p['name']} | {label} | {a:.2f} | {b:.2f} | {a/b:.3f}× | 2 | Candidate faster in {wins}/2 pairs. [Samples](benchmarks/profiles/named-key-union/{archive}) |")
table = here.parents[2] / "PERF.md"
assert all(row not in table.read_text() for row in rows)
(here/archive).write_bytes(gzip.compress(data, mtime=0))
with table.open("a") as f:
    f.write("\n".join(rows)+"\n")
print(*rows, sep="\n")
