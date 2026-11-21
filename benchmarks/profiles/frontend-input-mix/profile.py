"""Group sampled CPU in GetSourceFile by input class on fresh list-files runs."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
root = here.parents[2]
binary, pprof = (Path(s).resolve() for s in sys.argv[1:])
classes = {"compiler library","node_modules / declaration","node_modules / other input",
           "project or workspace / declaration","project or workspace / other input"}
def parse(raw):
    samples = raw.split("Locations\n",1)[0]
    total = 0
    groups = Counter()
    ns = None
    labelled = False
    for line in samples.splitlines():
        sample = re.match(r"^\s*\d+\s+(\d+):\s*[\d ]+$",line)
        if sample:
            ns = int(sample[1])
            total += ns
            labelled = False
        elif "source-input:" in line:
            label = re.fullmatch(r"\s*source-input:\[(.+)\]\s*",line)
            assert ns is not None and label and not labelled and label[1] in classes, line
            groups[label[1]] += ns
            labelled = True
    assert 0 < sum(groups.values()) <= total
    return dict(totalCpuNs=total,sourceLoadingNs=dict(groups))
result = {"observerSha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"projects":{}}
for group in ("small","large"):
    ref = json.loads((root / f"benchmarks/results/native-project-inlining/{group}.json").read_text())
    env = {k:v for k,v in os.environ.items() if k not in ref["environment"]["unsetEnvironment"]
           and not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
    env.update(ref["environment"]["compilerEnvironment"])
    for p in ref["projects"]:
        cwd = Path(p["cwd"])
        expected = sorted(str((cwd / f["file"]).resolve()) for f in p["preflight"]["candidate"]["inputs"])
        trials = []
        for run in range(3 if group=="small" else 1):
            with tempfile.TemporaryDirectory() as tmp:
                r=subprocess.run([binary,*p["fileDiscoveryArgs"]["candidate"],"--pprofDir",tmp],
                                 cwd=cwd,env=env,capture_output=True,text=True,timeout=300,check=True)
                assert not r.stderr,r.stderr
                files=[line for line in r.stdout.splitlines() if line and not line.startswith(("CPU profile: ","Memory profile: "))]
                assert sorted(str((cwd/f).resolve()) for f in files)==expected,p["name"]
                matches=list(Path(tmp).glob("*-cpuprofile.pb.gz"))
                assert len(matches)==1, list(Path(tmp).iterdir())
                profile=matches[0]
                saved = here / f"{p['name']}-{run}.pb.gz"
                saved.write_bytes(profile.read_bytes())
                raw=subprocess.check_output([pprof,"-raw",binary,profile],text=True)
                trial=parse(raw)
                tags=subprocess.check_output([pprof,"-tags","-unit=nanoseconds",binary,profile],text=True)
                labelled={kind:int(ns) for ns,kind in re.findall(r"^\s*(\d+)ns \([^)]*\): (.+)$",tags,re.M)}
                assert labelled==trial["sourceLoadingNs"]
                assert f"of {trial['totalCpuNs']}ns" in tags
                trial["profileSha256"]=hashlib.sha256(saved.read_bytes()).hexdigest()
                trials.append(trial)
        result["projects"][p["name"]] = dict(commit=p["commit"],inputCount=len(expected),trials=trials)
        print(p["name"], trials, flush=True)
(here/"cpu.json").write_text(json.dumps(result,indent=2)+"\n")
