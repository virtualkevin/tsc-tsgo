"""Check the nested operation trace on generated handlers and pinned Sentry."""
from pathlib import Path
import json
import os
import hashlib
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects
binary = Path(sys.argv[1]).resolve()
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2]/"upstream/typescript-go/internal/bundled/libs")
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
          "codes":{"U":"union worker","O":"object worker","P":"parameter worker","R":"reference worker",
                   "?":"other worker","C":"active mapper cache hit","r":"interned reference hit",
                   "h":"object instantiation table hit","m":"object instantiation table miss","u":"normalize mapped union"}}
with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp)/"main.ts"
    subprocess.run([sys.executable,here.parent/"instantiated-symbol-reuse/handlers.py",source,"1024","--array"],check=True)
    r = subprocess.run([binary,"--strict","--skipLibCheck","--noEmit","--pretty","false",source.name],
                       cwd=tmp,env=env,capture_output=True,check=True)
    assert not r.stdout
    report["handlers1024"] = json.loads(r.stderr)
    assert sum(report["handlers1024"].values()) == 1024
    print("handlers1024",report["handlers1024"],flush=True)
for name,commit,rows in observed_projects(binary,projects={"sentry"}):
    report[name] = {"commit":commit,"paths":dict(sorted(rows.items(),key=lambda kv:-kv[1]))}
    print(name,list(report[name]["paths"].items())[:4],flush=True)
(here/"trace.json").write_text(json.dumps(report,indent=2)+"\n")
