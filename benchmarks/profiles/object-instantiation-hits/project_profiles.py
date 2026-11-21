"""Profile the compared Go builds on the same pinned Sentry project."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
ref = json.loads(gzip.decompress((here.parent/"flow-declaration-runs/release.json.gz").read_bytes()))
p = next(p for p in ref["projects"] if p["name"]=="sentry")
cwd = Path(p["cwd"])
assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()
inputs = p["preflight"]["candidate"]["inputs"]
for f in inputs:
    assert sha(cwd/f["file"])==f["sha256"]
env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])
report={"commit":p["commit"],"inputs":len(inputs),"args":p["compilerArgs"]["candidate"],"binaries":{}}
for name,binary in zip(("control","candidate"),(Path(x).resolve() for x in sys.argv[1:]),strict=True):
    entry={"sha256":sha(binary)}
    with tempfile.TemporaryDirectory() as tmp:
        r=subprocess.run([binary,*report["args"],"--pprofDir",tmp],cwd=cwd,env=env,capture_output=True,text=True,check=True,timeout=480)
        assert not r.stderr and len(r.stdout.splitlines())==2 and all(l.startswith(("CPU profile: ","Memory profile: ")) for l in r.stdout.splitlines())
        for kind in ("cpu","mem"):
            f,=Path(tmp).glob(f"*-{kind}profile.pb.gz")
            out=here/f"sentry-{name}-{kind}.pb.gz"
            out.write_bytes(f.read_bytes())
            entry[kind]=sha(out)
    report["binaries"][name]=entry
    print(name,entry,flush=True)
(here/"profiles.json").write_text(json.dumps(report,indent=2)+"\n")
