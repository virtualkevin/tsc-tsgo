"""Verify the union/array repeat signature and public-release declaration output."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
observer, go, public = [Path(x).resolve() for x in sys.argv[1:]]
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2]/"upstream/typescript-go/internal/bundled/libs")
flags = ["--strict","--skipLibCheck","--pretty","false"]
report = {"flags":flags,"binarySha256":{k:hashlib.sha256(p.read_bytes()).hexdigest()
                                      for k,p in (("observer",observer),("go",go),("public",public))},"widths":{}}
with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    for n in (64,256,1024):
        source = d/"main.ts"
        subprocess.run([sys.executable,here/"generate.py",source,str(n)],check=True)
        traced = subprocess.run([observer,*flags,"--noEmit",source.name],cwd=d,env=env,capture_output=True,check=True)
        assert not traced.stdout
        counts = json.loads(traced.stderr)
        assert counts == {"union/*checker.ArrayTypeMapper":[n-1,3*(n-1),0,0,0]}
        outputs = []
        for k,b in (("go",go),("public",public)):
            r = subprocess.run([b,*flags,"--declaration","--emitDeclarationOnly","--outDir",k,source.name],cwd=d,env=env,capture_output=True,check=True)
            assert not r.stdout and not r.stderr
            outputs.append((d/k/"main.d.ts").read_bytes())
        assert outputs[0] == outputs[1]
        report["widths"][n] = {"counts":counts, "inputSha256":hashlib.sha256(source.read_bytes()).hexdigest(),
                               "declarationSha256":hashlib.sha256(outputs[0]).hexdigest()}
(here/"reduced.json").write_text(json.dumps(report,indent=2)+"\n")
