"""Fresh full-check processes on keys alternating between matched and retained."""
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory
import argparse
import hashlib
import json
import os
import subprocess
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("native", type=Path)
parser.add_argument("control", type=Path)
parser.add_argument("candidate", type=Path)
parser.add_argument("sizes", nargs="*", type=int, default=[4096, 32768, 131072])
parser.add_argument("--case", choices=("template", "intersection"), default="template")
parser.add_argument("--blocks", type=int, default=3)
parser.add_argument("--output", type=Path, default=here/"scaling.json")
args = parser.parse_args()
if args.blocks <= 0 or args.blocks % 3:
    parser.error("Choose a positive multiple of three blocks to balance compiler order.")
binaries = {role:getattr(args,role).resolve() for role in ("native","control","candidate")}
sizes = args.sizes
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
        if args.case == "intersection":
            # Sorted inputs interleave. Multiples of six belong to both unions.
            left = " | ".join(f'"k{i:06}"' for i in range(0, size, 2))
            right = " | ".join(f'"k{i:06}"' for i in range(0, size, 3))
            source = (f'type A = {left};\ntype B = {right};\ntype Allowed = A & B;\n'
                      'const retained: Allowed = "k000006";\n')
            invalid = 'const invalid: Allowed = "k000002";\n'
        else:
            keys = " | ".join(f'"k{i:06}{"yes" if i%2==0 else "no"}"' for i in range(size))
            source = ('type Keys = '+keys+';\ntype Allowed = Keys | `${string}yes`;\n'
                      'const retained: Allowed = "k000001no";\nconst pattern: Allowed = "outsideyes";\n')
            invalid = 'const invalid: Allowed = "outsideno";\n'
        path.write_text(source + invalid)
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
        for i in range(-1,args.blocks):
            start = max(i,0) % len(roles)
            order = roles[start:]+roles[:start]
            block={}
            for role in order:
                elapsed, run = check(role)
                assert run.returncode==0 and not (run.stdout or run.stderr), (role,run)
                block[role]=elapsed
            if i>=0: blocks.append(block)
        medians = {k:median(row[k] for row in blocks) for k in roles}
        report["projects"].append(dict(members=size,sourceSha256=sha(source.encode()),diagnosticSha256=sha(messages[0]),blocksMs=blocks,medianMs=medians))
        print(size, medians, flush=True)
args.output.write_text(json.dumps(report,indent=2)+"\n")
