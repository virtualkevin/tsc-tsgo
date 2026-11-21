"""Collect full cold-check profiles of the shipped compiler on verified inputs."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
root = here.parents[2]
ref = json.loads(gzip.decompress((here.parent / "literal-union-intersection/native.json.gz").read_bytes()))
binary = Path(ref["binaries"]["candidate"]["path"])
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(binary) == ref["binaries"]["candidate"]["sha256"]
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])
report = {"binarySha256":sha(binary), "projects":{}}
for p in sorted(ref["projects"], key=lambda p: len(p["preflight"]["candidate"]["inputs"])):
    cwd = Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip() == p["commit"]
    inputs = p["preflight"]["candidate"]["inputs"]
    for entry in inputs:
        assert sha(cwd / entry["file"]) == entry["sha256"]
    with tempfile.TemporaryDirectory() as tmp:
        run = subprocess.run([binary,*p["compilerArgs"]["candidate"],"--pprofDir",tmp],
                             cwd=cwd,env=env,capture_output=True,text=True,timeout=400,check=True)
        assert not run.stderr and all(line.startswith(("CPU profile: ", "Memory profile: ")) for line in run.stdout.splitlines())
        samples = {}
        for kind in ("cpu","mem"):
            paths = list(Path(tmp).glob(f"*-{kind}profile.pb.gz"))
            assert len(paths)==1, list(Path(tmp).iterdir())
            target = here / f"{p['name']}-{kind}.pb.gz"
            target.write_bytes(paths[0].read_bytes())
            samples[kind] = sha(target)
    report["projects"][p["name"]] = dict(commit=p["commit"],fileCount=len(inputs),profiles=samples)
    print(p["name"],samples,flush=True)
(here/"manifest.json").write_text(json.dumps(report,indent=2)+"\n")
