"""Fresh full-check processes on keys alternating between matched and retained."""
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
import hashlib
import json
import os
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
binaries = {name: Path(arg).resolve() for name,arg in zip(("native","control","candidate"), sys.argv[1:4], strict=True)}
sizes = list(map(int,sys.argv[4:])) or [4096,32768,131072]
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(root/"upstream/typescript-go/internal/bundled/libs")
def sha(data):
    return hashlib.sha256(data).hexdigest()

report = {"binarySha256":{k:sha(v.read_bytes()) for k,v in binaries.items()}, "projects":[]}
with TemporaryDirectory() as folder:
    path = Path(folder)/"keys.ts"
    def check(role):
        start = time.perf_counter_ns()
        run = subprocess.run([binaries[role], "--ignoreConfig", "--strict", "--lib", "es5", "--noEmit", "--pretty", "false", path.name],
                             cwd=folder, env=env, capture_output=True, timeout=180)
        return (time.perf_counter_ns()-start)/1e6, run
    for size in sizes:
        keys = " | ".join(f'"k{i:06}{"yes" if i%2==0 else "no"}"' for i in range(size))
        source = ('type Keys = '+keys+';\ntype Allowed = Keys | `${string}yes`;\n'
                  'const retained: Allowed = "k000001no";\nconst pattern: Allowed = "outsideyes";\n')
        path.write_text(source+'const invalid: Allowed = "outsideno";\n')
        messages=[]
        for role in binaries:
            _, run = check(role)
            assert run.returncode and b"error TS2322" in run.stdout, (role,run)
            assert not run.stderr
            messages.append(run.stdout)
        assert len(set(messages))==1
        path.write_text(source)
        blocks=[]
        roles=list(binaries)
        for i in range(-1,3):
            order=roles if i<0 else roles[i:]+roles[:i]
            block={}
            for role in order:
                elapsed, run = check(role)
                assert run.returncode==0 and not (run.stdout or run.stderr), (role,run)
                block[role]=elapsed
            if i>=0: blocks.append(block)
        medians = {k:median(row[k] for row in blocks) for k in roles}
        report["projects"].append(dict(members=size,sourceSha256=sha(source.encode()),diagnosticSha256=sha(messages[0]),blocksMs=blocks,medianMs=medians))
        print(size, medians, flush=True)
(here/"scaling.json").write_text(json.dumps(report,indent=2)+"\n")
