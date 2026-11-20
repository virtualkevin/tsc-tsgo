"""Record candidate-first confirmation. Harness baseline = advised; candidate = control."""
import gzip
import hashlib
import json
from pathlib import Path
from statistics import median
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
source = Path(sys.argv[1])
data = json.loads(source.read_bytes())
assert data["status"] == "passed" and data["warmups"] == 1
assert data["environment"]["candidateEnvironmentOverrides"] == {}
builds = json.loads((here / "builds.json").read_text())["builds"]
for mode, name in (("baseline","advised"), ("candidate","control")):
    binary = Path(data["binaries"][mode]["path"])
    assert binary.name == name
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == data["binaries"][mode]["sha256"] == builds[name]["sha256"]
pilot_path = here.parent / "native-go-discovery" / (source.name + ".gz")
pilot = json.loads(gzip.decompress(pilot_path.read_bytes()))
archive = here / (source.name + ".gz")
assert not archive.exists()
rows = []
for p, prior in zip(data["projects"], pilot["projects"], strict=True):
    assert p["name"] == prior["name"] and p["commit"] == prior["commit"]
    assert p["status"] == "passed" and p["resourceWrapperVerifiedAfter"] and p["diagnosticCount"] == 0
    assert p["preflight"]["candidate"]["inputs"] == prior["preflight"]["baseline"]["inputs"] == p["preflight"]["baseline"]["inputs"]
    assert p["compilerArgs"]["candidate"] == p["compilerArgs"]["baseline"] == prior["compilerArgs"]["candidate"]
    pairs = p["pairs"]
    assert len(pairs) == data["runs"] >= 4
    for i, pair in enumerate(pairs):
        assert pair["order"] == (["candidate","baseline"] if i % 2 else ["baseline","candidate"])
    c, a = [median(s[m] for s in pairs) for m in ("candidate","baseline")]
    ratios = [s["candidate"]/s["baseline"] for s in pairs]
    print(p["name"], "control/advised", c/a, "pairs", ratios, flush=True)
    rows.append(f"| Matched heap huge-page confirmation | {p['name']} | Rebuilt Go control | {c:.2f} | {a:.2f} | {c/a:.3f}× | {len(pairs)} | Advised first in opening pair. Paired median {median(ratios):.3f}×. [Samples]({archive.relative_to(root)}) |")
raw = source.read_bytes()
archive.write_bytes(gzip.compress(raw,mtime=0))
assert gzip.decompress(archive.read_bytes()) == raw
with (root/"PERF.md").open("a") as f:
    f.write("\n".join(rows)+"\n")
