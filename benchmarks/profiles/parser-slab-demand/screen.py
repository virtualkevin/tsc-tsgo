"""Check cold program construction and report allocation counts independently of timing."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import time

here=Path(__file__).resolve().parent
ref=json.loads(gzip.decompress((here.parent/"template-union-compaction/native.json.gz").read_bytes()))
bins={k:Path(v).resolve() for k,v in zip(("control","candidate"),sys.argv[1:3],strict=True)}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])
report={"binarySha256":{k:sha(v) for k,v in bins.items()},"projects":{}}
for project in sorted(ref["projects"],key=lambda p:len(p["preflight"]["candidate"]["inputs"])):
    cwd=Path(project["cwd"])
    name=project["name"]
    expected=sorted(str((cwd/i["file"]).resolve()) for i in project["preflight"]["candidate"]["inputs"])
    for i in project["preflight"]["candidate"]["inputs"]:assert sha(cwd/i["file"])==i["sha256"]
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==project["commit"]
    def run(role,extra):
        start=time.monotonic_ns()
        r=subprocess.run([bins[role],*project["fileDiscoveryArgs"]["candidate"],*extra],cwd=cwd,env=env,
                         capture_output=True,text=True,check=True,timeout=300)
        elapsed=(time.monotonic_ns()-start)/1e6
        assert not r.stderr
        lines=r.stdout.splitlines()
        assert sorted(str((cwd/f).resolve()) for f in lines[:len(expected)])==expected
        if not extra:assert len(lines)==len(expected)
        return elapsed,"\n".join(lines[len(expected):])
    counters={}
    for role in bins:
        _,stats=run(role,["--extendedDiagnostics"])
        counters[role]={k:int(v) for k,v in re.findall(r"^(Files|Lines|Identifiers|Symbols|Types|Instantiations|Memory used|Memory allocs):\s*(\d+)K?\s*$",stats,re.M)}
        assert len(counters[role])==8
    for k in ("Files","Lines","Identifiers","Types","Instantiations"):
        assert counters["control"][k]==counters["candidate"][k]
    samples=[]
    for i in range(-1,4):
        order=("candidate","control") if i>=0 and i%2 else ("control","candidate")
        block={role:run(role,[])[0] for role in order}
        if i>=0:samples.append(block)
    medians={k:statistics.median(s[k] for s in samples) for k in bins}
    report["projects"][name]=dict(commit=project["commit"],files=len(expected),extendedDiagnostics=counters,
                                  blocksMs=samples,medianMs=medians)
    print(name,medians,counters,flush=True)
output=Path(sys.argv[3]) if len(sys.argv)>3 else here/"discovery.json"
output.write_text(json.dumps(report,indent=2)+"\n")
