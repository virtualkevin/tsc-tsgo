"""Run two fresh address-sampled checker processes for each verified workload."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
ref = json.loads(gzip.decompress((here.parent / "literal-union-intersection/native.json.gz").read_bytes()))
binary = Path(sys.argv[1]).resolve()
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])
report = {"probeSha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
          "categories":["occupiedHit","emptyMiss","rehashInsert"], "projects":{}}
for p in sorted(ref["projects"],key=lambda p:len(p["preflight"]["candidate"]["inputs"])):
    cwd = Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip() == p["commit"]
    for item in p["preflight"]["candidate"]["inputs"]:
        assert hashlib.sha256((cwd / item["file"]).read_bytes()).hexdigest() == item["sha256"]
    blocks = []
    for _ in range(2):
        r = subprocess.run([binary,*p["compilerArgs"]["candidate"]],cwd=cwd,env=env,capture_output=True,text=True,timeout=480,check=True)
        assert not r.stdout
        counts = json.loads(r.stderr)
        block = {}
        for key,values in zip(report["categories"], counts, strict=True):
            assert len(values)==17 and all(isinstance(x,int) and x>=0 for x in values)
            bins, steps = values[:16], values[16]
            assert sum(bins)>0 and sum((i+1)*n for i,n in enumerate(bins))<=steps
            block[key] = dict(histogram=bins,totalProbes=steps,meanProbes=steps/sum(bins),firstSlotFraction=bins[0]/sum(bins))
        blocks.append(block)
        print(p["name"], [(k,round(v["meanProbes"],2),round(v["firstSlotFraction"],3)) for k,v in block.items()],flush=True)
    report["projects"][p["name"]] = dict(commit=p["commit"],blocks=blocks)
(Path(sys.argv[2]) if len(sys.argv)>2 else here/"probe-counts.json").write_text(json.dumps(report,indent=2)+"\n")
