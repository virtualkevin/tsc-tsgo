"""Measure the release builds' noEmit stage on the two declaration workloads."""
import hashlib
import json
import re
import subprocess
import sys
import os
from pathlib import Path

here = Path(__file__).resolve().parent
base = json.loads(Path(sys.argv[1]).read_text())
assert base["status"] == "passed"
env = {k:v for k,v in os.environ.items() if not k.startswith(("SCRIPTC_","TSC_","TS_GO_","GODEBUG","GOMAXPROCS","GOGC","GOMEMLIMIT"))}
env.update(base["environment"]["compilerEnvironment"])
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
report = {"binarySha256":{k:v["sha256"] for k,v in base["binaries"].items()},"projects":{}}
for p in base["projects"]:
    cwd = Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
    expected = p["preflight"]["baseline"]["inputs"]
    assert expected == p["preflight"]["candidate"]["inputs"]
    assert all(sha(cwd/f["file"])==f["sha256"] for f in expected)
    samples = []
    for order in (("baseline","candidate"),("candidate","baseline"),("baseline","candidate"),("candidate","baseline")):
        for name in order:
            b=base["binaries"][name]
            assert sha(b["path"])==b["sha256"]
            r=subprocess.run([b["path"],*p["compilerArgs"][name],"--extendedDiagnostics"],cwd=cwd,env=env,
                             capture_output=True,text=True,check=True,timeout=180)
            assert not r.stderr and not re.search(r"error TS\d+",r.stdout)
            assert int(re.search(r"^Files:\s*(\d+)$",r.stdout,re.M)[1])==len(expected)
            samples.append({"engine":name,"emitSeconds":float(re.search(r"^Emit time:\s*([\d.]+)s$",r.stdout,re.M)[1]),"stdout":r.stdout})
    report["projects"][p["name"]] = {"commit":p["commit"],"files":len(expected),"samples":samples}
(here/"emit-phase.json").write_text(json.dumps(report,indent=2)+"\n")
