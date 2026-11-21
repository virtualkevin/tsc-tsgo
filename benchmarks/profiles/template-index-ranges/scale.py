"""Time fresh compiler processes on equal template-index inputs in rotating order."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument("--binary", nargs=2, action="append", metavar=("NAME", "FILE"), required=True)
parser.add_argument("--width", nargs="+", type=int, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
generator = root / "benchmarks/profiles/template-index-text/generate.py"
programs = {name: Path(path).absolute() for name, path in args.binary}
env = {key: value for key, value in os.environ.items() if not key.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(root / "upstream/typescript-go/internal/bundled/libs")
flags = ["--noEmit", "--strict", "--skipLibCheck", "--pretty", "false", "--target", "es2022", "matrix.ts"]
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
report = {"flags":flags, "binaries":{}, "widths":{}}
for name, path in programs.items():
    version = subprocess.check_output([path, "--version"], env=env, text=True).strip()
    report["binaries"][name] = {"path":str(path), "version":version, "sha256":digest(path)}
with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / "matrix.ts"
    for width in args.width:
        subprocess.run([sys.executable, generator, source, str(width)], check=True)
        result = {"inputSha256":digest(source), "samplesMs":[]}
        report["widths"][width] = result
        names = list(programs)
        for i in range(len(names)+1):
            order = names[i % len(names):] + names[:i % len(names)]
            sample = {}
            for name in order:
                before = time.perf_counter_ns()
                r = subprocess.run([programs[name], *flags], cwd=tmp, env=env, capture_output=True, timeout=240)
                sample[name] = (time.perf_counter_ns()-before)/1e6
                if r.returncode or r.stdout or r.stderr:
                    raise RuntimeError((name, width, r.returncode, r.stdout[:600], r.stderr[:600]))
            if i == 0:
                result["warmupMs"] = sample
            else:
                result["samplesMs"].append(sample)
            print(width, sample, flush=True)
        args.output.write_text(json.dumps(report, indent=2)+"\n")
