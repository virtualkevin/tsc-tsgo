"""Time the capacity candidate and matched ordinary Go on the frozen projects."""
import gzip
import hashlib
import json
from pathlib import Path
from statistics import median
import subprocess
import sys

here = Path(__file__).resolve().parent
repo = here.parents[2]
control, candidate, output = (Path(arg).resolve() for arg in sys.argv[1:])
manifest = json.loads((here / "profiles.json").read_text())
for role, binary in (("control", control), ("candidate", candidate)):
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == manifest["binaries"][role]["sha256"]
ref = json.loads(gzip.decompress((here.parent / "ordered-intersection-pair/screen.json.gz").read_bytes()))
subprocess.run(["node", "benchmarks/run.mjs", "--baseline", control, "--candidate", candidate,
                "--projects", "vscode,sentry,typeorm,trpc", "--runs", "2", "--warmups", "0",
                "--measure-rss", "--output", output], cwd=repo, check=True)
data = output.read_bytes()
result = json.loads(data)
assert result["status"] == "passed" and result["environment"]["compilerEnvironment"] == ref["environment"]["compilerEnvironment"]
assert result["binaries"]["baseline"]["sha256"] == manifest["binaries"]["control"]["sha256"]
assert result["binaries"]["candidate"]["sha256"] == manifest["binaries"]["candidate"]["sha256"]
rows = []
for project, prior in zip(result["projects"], ref["projects"], strict=True):
    assert (project["name"], project["commit"], project["compilerArgs"]) == (prior["name"], prior["commit"], prior["compilerArgs"])
    assert project["preflight"]["candidate"]["inputs"] == project["preflight"]["baseline"]["inputs"] == prior["preflight"]["baseline"]["inputs"]
    assert project["status"] == "passed" and project["diagnosticCount"] == 0 and project["resourceWrapperVerifiedAfter"]
    pairs = project["pairs"]
    assert [p["order"] for p in pairs] == [["baseline", "candidate"], ["candidate", "baseline"]]
    a,b = (median(r[k] for r in pairs) for k in ("baseline", "candidate"))
    wins = sum(r["baseline"] > r["candidate"] for r in pairs)
    rows.append(f"| Size inherited member tables from previous layout | {project['name']} | Matched ordinary Go build | {a:.2f} | {b:.2f} | {a/b:.3f}× | 2 | Candidate faster in {wins}/2 pairs. [Samples](benchmarks/profiles/inherited-member-capacity/screen.json.gz) |")
table = repo / "PERF.md"
assert len(rows) == 4 and all(r not in table.read_text() for r in rows)
(here / "screen.json.gz").write_bytes(gzip.compress(data, mtime=0))
with table.open("a") as f:
    f.write("\n".join(rows) + "\n")
print(*rows, sep="\n")
