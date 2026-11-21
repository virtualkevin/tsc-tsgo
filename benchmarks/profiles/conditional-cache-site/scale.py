"""Compare whole-program type checks on the reduced Extract case."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
here=Path(__file__).resolve().parent
root=here.parents[2]
go,public,observer=map(lambda s:Path(s).absolute(),sys.argv[1:4])
env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
env["TSC_TS_LIB_DIR"]=str(root/"upstream/typescript-go/internal/bundled/libs")
args=["--skipLibCheck","--strict","--pretty","false","--noEmit","main.ts"]
binary={"go":go,"public":public}
report={"flags":args,"binaries":{},"widths":{}}
for k,b in binary.items():
    report["binaries"][k]={"version":subprocess.check_output([b,"--version"],text=True,env=env).strip(),"sha256":hashlib.sha256(b.read_bytes()).hexdigest()}
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/"main.ts"
    for n in (64,128,256,512):
        subprocess.run([sys.executable,here/"generate.py",p,str(n)],check=True)
        row={"inputSha256":hashlib.sha256(p.read_bytes()).hexdigest(),"pairs":[]}
        report["widths"][n]=row
        observed=subprocess.run([observer,*args],cwd=d,env=env,capture_output=True,check=True,timeout=180)
        assert not observed.stdout
        events=json.loads(observed.stderr)
        row["observedMasks"]={f"{i},{j}":v for i,a in enumerate(events["rows"]) for j,v in enumerate(a) if v}
        assert row["observedMasks"]=={"4,32":n,"8,32":n*n-n}
        for i in range(5):
            order=list(binary) if i%2 else list(reversed(binary))
            pair={}
            for k in order:
                start=time.perf_counter_ns()
                r=subprocess.run([binary[k],*args],cwd=d,env=env,capture_output=True,check=True,timeout=240)
                pair[k]=(time.perf_counter_ns()-start)/1e6
                assert not r.stdout and not r.stderr
            if i: row["pairs"].append(pair)
            else: row["warmup"]=pair
        print(n,{k:statistics.median(x[k] for x in row["pairs"]) for k in binary},flush=True)
        (here/"scale.json").write_text(json.dumps(report,indent=2)+"\n")
