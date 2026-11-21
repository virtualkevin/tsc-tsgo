"""Verify the union/array repeat signature and public-release declaration output."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

here = Path(__file__).resolve().parent
observer, go, public = [Path(x).resolve() for x in sys.argv[1:4]]
handlers = sys.argv[4:] == ["--handlers"]
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2]/"upstream/typescript-go/internal/bundled/libs")
flags = ["--strict","--skipLibCheck","--pretty","false"]
report = {"flags":flags,"binarySha256":{k:hashlib.sha256(p.read_bytes()).hexdigest()
                                      for k,p in (("observer",observer),("go",go),("public",public))},"widths":{}}
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    for n in ((256,1024,4096) if handlers else (64,256,1024)):
        source = d/"main.ts"
        subprocess.run([sys.executable,here/("handlers.py" if handlers else "generate.py"),source,str(n)],check=True)
        traced = subprocess.run([observer,*flags,"--noEmit",source.name],cwd=d,env=env,capture_output=True,check=True)
        assert not traced.stdout
        counts = json.loads(traced.stderr)
        if handlers:
            assert counts == {"atom=Undefined member=Object alias=ReactEventHandler ref= nested=4":[n-1,4*(n-1),0,0,0]}
        else:
            assert counts == {"union/*checker.ArrayTypeMapper":[n-1,3*(n-1),0,0,0]}
        outputs = []
        for k,b in (("go",go),("public",public)):
            r = subprocess.run([b,*flags,"--declaration","--emitDeclarationOnly","--outDir",k,source.name],cwd=d,env=env,capture_output=True,check=True)
            assert not r.stdout and not r.stderr
            outputs.append((d/k/"main.d.ts").read_bytes())
        assert outputs[0] == outputs[1]
        report["widths"][n] = {"counts":counts, "inputSha256":hashlib.sha256(source.read_bytes()).hexdigest(),
                               "declarationSha256":hashlib.sha256(outputs[0]).hexdigest()}
        if handlers:
            pairs = []
            bins = {"go":go,"public":public}
            for i in range(5):
                pair = {}
                for k in (bins if i % 2 else reversed(bins)):
                    start = time.perf_counter_ns()
                    r = subprocess.run([bins[k],*flags,"--noEmit",source.name],cwd=d,env=env,capture_output=True,check=True)
                    pair[k] = (time.perf_counter_ns()-start)/1e6
                    assert not r.stdout and not r.stderr
                if i:
                    pairs.append(pair)
                else:
                    report["widths"][n]["warmup"] = pair
            report["widths"][n]["pairs"] = pairs
(here/("handlers.json" if handlers else "reduced.json")).write_text(json.dumps(report,indent=2)+"\n")
