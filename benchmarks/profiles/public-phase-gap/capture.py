"""Compare phase reports from full checks against the published 0.0.2 release."""
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

here = Path(__file__).resolve().parent
ref = json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
env = {k:v for k,v in os.environ.items() if not k.startswith(("SCRIPTC_","TSC_","TS_GO_","GODEBUG","GOMAXPROCS","GOGC","GOMEMLIMIT"))}
env.update(ref["environment"]["compilerEnvironment"])
binaries = dict(zip(("public","go"), sys.argv[1:], strict=True))
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
report = {"libraryDirectory":env["TSC_TS_LIB_DIR"],"executables":{k:{"path":v,"sha256":digest(v)} for k,v in binaries.items()},"projects":{}}
for p in sorted(ref["projects"],key=lambda p:len(p["preflight"]["baseline"]["inputs"])):
    cwd = Path(p["cwd"])
    inputs = p["preflight"]["baseline"]["inputs"]
    assert inputs == p["preflight"]["candidate"]["inputs"]
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
    def verify():
        assert all(digest(cwd/i["file"])==i["sha256"] for i in inputs)
    verify()
    args = p["compilerArgs"]["candidate"]
    assert args == p["compilerArgs"]["baseline"] and args[args.index("--noCheck")+1]=="false"
    for binary in binaries.values():
        result = subprocess.run([binary,*args,"--listFilesOnly"],cwd=cwd,env=env,text=True,capture_output=True,check=True,timeout=480)
        assert not result.stderr
        assert sorted(os.path.relpath(cwd/x,cwd) for x in result.stdout.splitlines())==sorted(i["file"] for i in inputs)
    samples = []
    for order in (("public","go"),("go","public")):
        for engine in order:
            start = time.perf_counter_ns()
            proc = subprocess.run([binaries[engine],*args,"--extendedDiagnostics"],cwd=cwd,env=env,text=True,capture_output=True,check=True,timeout=480)
            elapsed = (time.perf_counter_ns()-start)/1e9
            assert not proc.stderr and not re.search(r"error TS\d+",proc.stdout)
            assert int(re.search(r"^Files:\s*(\d+)$",proc.stdout,re.M)[1])==len(inputs)
            phases = {k:float(v) for k,v in re.findall(r"^(Config|Parse|Bind|Check|Emit|Total) time:\s*([\d.]+)s$",proc.stdout,re.M)}
            assert set(phases)=={"Config","Parse","Bind","Check","Emit","Total"}
            samples.append(dict(engine=engine, wall=elapsed, phases=phases, stdout=proc.stdout))
    verify()
    medians = {}
    for engine in binaries:
        rows = [s for s in samples if s["engine"]==engine]
        medians[engine] = {k:statistics.median(s["phases"][k] for s in rows) for k in phases}
        medians[engine]["wall"] = statistics.median(s["wall"] for s in rows)
    report["projects"][p["name"]] = dict(commit=p["commit"], files=len(inputs),args=args,
                                           fileListSha256=p["preflight"]["baseline"]["fileListSha256"],samples=samples,medians=medians)
    print(p["name"],medians,flush=True)
assert all(digest(v["path"])==v["sha256"] for v in report["executables"].values())
(here/"results.json").write_text(json.dumps(report,indent=2)+"\n")
