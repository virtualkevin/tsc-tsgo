"""Time pinned Sentry directly against the original npm launcher and platform binary."""
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

here=Path(__file__).resolve().parent
repo=here.parents[2]
old=here.parent/"jsx-absent-discriminants"
identity=json.loads((old/"groups-public-package.json").read_text())["packages"]
ref=json.loads(gzip.decompress((old/"groups-public.json.gz").read_bytes()))
launcher=Path(ref["binaries"]["baseline"]["path"])
candidate=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]).resolve()
def verify():
    for package,entry in identity.items():
        path=Path(entry["executable"])
        assert json.loads((path.parents[1]/"package.json").read_text())["version"]==entry["version"]=="0.0.2"
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry["sha256"]
    assert launcher.resolve()==Path(identity["tsc-ts"]["executable"])
verify()
subprocess.run(["node","benchmarks/run.mjs","--baseline",str(launcher),"--candidate",str(candidate),
                "--projects","sentry","--runs","2","--warmups","0","--measure-rss","--output",str(out)],cwd=repo,check=True)
verify()
data=out.read_bytes()
d=json.loads(data)
p,=d["projects"]
oldp,=ref["projects"]
assert d["binaries"]["baseline"]["sha256"]==identity["tsc-ts"]["sha256"]
assert d["binaries"]["candidate"]["sha256"]==json.loads((here/"key-parity.json").read_text())["binaries"]["candidate"]
assert d["status"]==p["status"]=="passed" and p["diagnosticCount"]==0 and p["resourceWrapperVerifiedAfter"]
assert p["commit"]==oldp["commit"] and p["compilerArgs"]==oldp["compilerArgs"]
assert p["preflight"]["baseline"]["inputs"]==p["preflight"]["candidate"]["inputs"]==oldp["preflight"]["baseline"]["inputs"]
assert [x["order"] for x in p["pairs"]]==[["baseline","candidate"],["candidate","baseline"]]
a,b=(statistics.median(x[k] for x in p["pairs"]) for k in ("baseline","candidate"))
row=f"| Reuse identical mapped key and name links | Sentry | Public npm tsc-ts@0.0.2 | {a:.2f} | {b:.2f} | {a/b:.3f}× | 2 | Launcher and native binary verified before and after comparison. [Samples](benchmarks/profiles/mapped-member-demand/public.json.gz) |"
assert row not in (repo/"PERF.md").read_text()
(here/"public.json.gz").write_bytes(gzip.compress(data,mtime=0))
with (repo/"PERF.md").open("a") as f:f.write(row+"\n")
print(row)
