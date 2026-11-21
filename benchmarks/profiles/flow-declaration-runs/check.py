"""Compare declarations, diagnostics and exit codes on healthy and erroneous flow inputs."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2]/"upstream/typescript-go/internal/bundled/libs")
bins = {k:Path(v).resolve() for k,v in zip(("baseline","candidate","public"),sys.argv[1:],strict=True)}
text = (here/"fixture.ts").read_text()
report = {"sha256":{k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in bins.items()}, "variants":{}}
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    for bad in (False,True):
        (d/"main.ts").write_text(text.replace("after.toUpperCase()","after.toFixed()") if bad else text)
        results = []
        for k,binary in bins.items():
            r = subprocess.run([binary,"--strict","--skipLibCheck","--pretty","false","--declaration",
                                "--emitDeclarationOnly","--outDir",k,"main.ts"],cwd=d,env=env,capture_output=True)
            assert not r.stderr and (bool(r.stdout) == bad) and (bool(r.returncode) == bad)
            results.append((r.returncode,r.stdout,(d/k/"main.d.ts").read_bytes()))
        assert results[0] == results[1] == results[2]
        status,output,decl = results[0]
        report["variants"][str(bad)] = {"exitCode":status,"stdout":output.decode(),"declarationSha256":hashlib.sha256(decl).hexdigest()}
(here/"checks.json").write_text(json.dumps(report,indent=2)+"\n")
