"""Compare instrumented lookup counts and checker work against the matched Go control."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
shadow = sys.argv[3:]==["--shadow"]
assert not sys.argv[3:] or shadow
compilers = {name:Path(path).resolve() for name,path in zip(("control","observer"), sys.argv[1:3],strict=True)}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = {"binarySha256":{k:digest(v) for k,v in compilers.items()},"projects":{}}
fields = ["calls","eligible","resolved","slotHits"]
if shadow:
    prior=json.loads((here/"counts.json").read_text())
    assert prior["binarySha256"]["control"]==report["binarySha256"]["control"]
    fields += ["differentType","changedWork"]
for group in ("small","large"):
    ref = json.loads((root/f"benchmarks/results/native-project-inlining/{group}.json").read_text())
    env = {k:v for k,v in os.environ.items() if k not in ref["environment"]["unsetEnvironment"]
           and not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
    env.update(ref["environment"]["compilerEnvironment"])
    for p in ref["projects"]:
        cwd = Path(p["cwd"])
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
        for f in p["preflight"]["candidate"]["inputs"]:
            assert digest(cwd/f["file"])==f["sha256"]
        work={}
        for role,binary in compilers.items():
            if shadow and role=="control":
                assert prior["projects"][p["name"]]["commit"]==p["commit"]
                work["control"]=prior["projects"][p["name"]]["work"]["control"]
                continue
            r=subprocess.run([binary,*p["args"],"--extendedDiagnostics"],cwd=cwd,env=env,timeout=400,
                             capture_output=True,text=True,check=True)
            assert not re.search(r"error TS\d+",r.stdout)
            work[role]={k:int(v) for k,v in re.findall(r"^(Files|Lines|Identifiers|Types|Symbols|Instantiations):\s*(\d+)\s*$",r.stdout,re.M)}
            assert len(work[role])==6
            if role=="observer":
                match=re.fullmatch(r"\[([\d ]+)\]\n",r.stderr)
                assert match,r.stderr
                counts=dict(zip(fields,map(int,match[1].split()),strict=True))
                assert max(counts["resolved"],counts["slotHits"])<=counts["eligible"]<=counts["calls"]
            else:
                assert not r.stderr
        report["projects"][p["name"]]=dict(commit=p["commit"],counts=counts,work=work)
        print(p["name"],counts,"work matches",work["control"]==work["observer"],flush=True)
(here/("shadow.json" if shadow else "counts.json")).write_text(json.dumps(report,indent=2)+"\n")
