"""Count object instantiation-table probes by arity, prior mapper and synthesized alias."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
          "maskBits":["cacheHit","priorMapper","synthesizedAlias"], "arityCap":5, "projects":{}, "handlers":{}}

def summarize(rows):
    counts = {}
    for i,row in enumerate(rows):
        for mask,n in enumerate(row):
            if n:
                counts[f"{i},{mask}"] = n
    total = sum(counts.values())
    hits = sum(n for i,row in enumerate(rows) for mask,n in enumerate(row) if mask & 1)
    small_hits = sum(n for i,row in enumerate(rows) for mask,n in enumerate(row) if mask & 1 and i <= 4)
    return {"counts":counts, "total":total, "hits":hits, "shortHits":small_hits}

env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2]/"upstream/typescript-go/internal/bundled/libs")
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp)/"main.ts"
    for n in (1,64,1024,4096):
        subprocess.run([sys.executable,here.parent/"instantiated-symbol-reuse/handlers.py",p,str(n),"--array"],check=True)
        r = subprocess.run([binary,"--strict","--skipLibCheck","--noEmit","--pretty","false",p.name],env=env,cwd=tmp,capture_output=True,check=True)
        assert not r.stdout
        report["handlers"][n] = summarize(json.loads(r.stderr))
        print("handlers", n, report["handlers"][n],flush=True)
for name,commit,rows in observed_projects(binary):
    report["projects"][name] = {"commit":commit, **summarize(rows)}
    print(name, {k:v for k,v in report["projects"][name].items() if k!="counts"},flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
