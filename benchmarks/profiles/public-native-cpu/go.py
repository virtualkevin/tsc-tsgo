"""Record Go CPU samples on the same frozen graph and public release libraries."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
timing = json.loads((here.parent/"void-callback/timings.json").read_text())
reference = json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
binary = Path(timing["executables"]["go"]["path"])
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert sha(binary) == timing["executables"]["go"]["sha256"]
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_","SCRIPTC_","TS_GO_","GODEBUG","GOMAXPROCS","GOMEMLIMIT","GOGC"))}
env.update(reference["environment"]["compilerEnvironment"])
report = {"executable":timing["executables"]["go"], "projects":{}}
for p in reference["projects"]:
    project = timing["projects"][p["name"]]
    cwd = Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==project["commit"]
    assert all(sha(cwd/entry["file"])==entry["sha256"] for entry in p["preflight"]["candidate"]["inputs"])
    with tempfile.TemporaryDirectory() as tmp:
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        run = subprocess.run([binary,*project["args"],"--pprofDir",tmp],cwd=cwd,env=env,capture_output=True,text=True,check=True,timeout=480)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        assert not run.stderr and len(run.stdout.splitlines())==2 and all(line.startswith(("Memory profile: ", "CPU profile: ")) for line in run.stdout.splitlines())
        profile, = Path(tmp).glob("*-cpuprofile.pb.gz")
        target = here/(p["name"]+"-go.pb.gz")
        target.write_bytes(profile.read_bytes())
        report["projects"][p["name"]] = dict(cpuProfileSha256=sha(target),commit=project["commit"],
            userCPUSeconds=after.ru_utime-before.ru_utime,systemCPUSeconds=after.ru_stime-before.ru_stime)
        print(p["name"], report["projects"][p["name"]],flush=True)
        (here/"go.json").write_text(json.dumps(report,indent=2)+"\n")
