"""Run a diagnostic compiler on the four frozen full-check workloads."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess

def observed_projects(binary):
    ref = json.loads(gzip.decompress((Path(__file__).resolve().parent/"literal-union-intersection/native.json.gz").read_bytes()))
    env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
    env.update(ref["environment"]["compilerEnvironment"])
    for p in sorted(ref["projects"],key=lambda p:len(p["preflight"]["candidate"]["inputs"])):
        cwd = Path(p["cwd"])
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip() == p["commit"]
        for f in p["preflight"]["candidate"]["inputs"]:
            assert hashlib.sha256((cwd/f["file"]).read_bytes()).hexdigest() == f["sha256"]
        r = subprocess.run([binary,*p["compilerArgs"]["candidate"]],cwd=cwd,env=env,capture_output=True,text=True,timeout=480,check=True)
        assert not r.stdout
        yield p["name"], p["commit"], json.loads(r.stderr)
