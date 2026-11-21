"""Compare fresh full checks with identical released libraries and verified inputs."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
ref = json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
binaries = dict(zip(("public", "go", "candidate"), sys.argv[1:], strict=True))
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "SCRIPTC_", "TS_GO_", "GODEBUG", "GOGC", "GOMAXPROCS", "GOMEMLIMIT"))}
env.update(ref["environment"]["compilerEnvironment"])
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

report = {"libraryDirectory":env["TSC_TS_LIB_DIR"], "executables":{
    engine:dict(path=path, sha256=digest(path)) for engine,path in binaries.items()
}, "projects":{}}
projects = sorted(ref["projects"], key=lambda p:len(p["preflight"]["candidate"]["inputs"]))
for i,project in enumerate(projects):
    cwd = Path(project["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip() == project["commit"]
    args = project["compilerArgs"]["candidate"]
    assert args == project["compilerArgs"]["baseline"] and args[args.index("--noCheck")+1] == "false"
    inputs = project["preflight"]["baseline"]["inputs"]
    assert inputs == project["preflight"]["candidate"]["inputs"]
    expected = sorted(i["file"] for i in inputs)
    def verify_inputs():
        assert all(digest(cwd/item["file"]) == item["sha256"] for item in inputs)
    verify_inputs()
    for binary in binaries.values():
        listed = subprocess.run([binary,*args,"--listFilesOnly"],cwd=cwd,env=env,text=True,capture_output=True,check=True,timeout=480)
        assert not listed.stderr and sorted(os.path.relpath(cwd/path,cwd) for path in listed.stdout.splitlines()) == expected
    order = list(binaries)
    order = order[i%3:] + order[:i%3]
    rows = []
    for engine in (*order,*reversed(order)):
        start = time.monotonic_ns()
        proc = subprocess.run([binaries[engine],*args],cwd=cwd,env=env,capture_output=True,check=True,timeout=480)
        elapsed = (time.monotonic_ns()-start)/1e6
        assert not proc.stdout and not proc.stderr
        rows.append(dict(engine=engine,wallMs=elapsed))
    verify_inputs()
    medians = {e:statistics.median(row["wallMs"] for row in rows if row["engine"]==e) for e in order}
    report["projects"][project["name"]] = dict(commit=project["commit"],files=len(expected),args=args,samples=rows,medianMs=medians)
    print(project["name"], medians, flush=True)
    (here/"timings.json").write_text(json.dumps(report,indent=2)+"\n")
assert all(digest(row["path"])==row["sha256"] for row in report["executables"].values())
