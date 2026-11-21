"""Time a matched Go build and the declaration-run candidate on the handler fixture."""
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

here = Path(__file__).resolve().parent
bins = dict(zip(("baseline", "candidate"), (Path(x).resolve() for x in sys.argv[1:3]), strict=True))
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2] / "upstream/typescript-go/internal/bundled/libs")
mode = sys.argv[3:] or ["--ordinary"]
outputs = {"--ordinary":"scale.json", "--public":"public.json", "--shipping-public":"shipping-public.json"}
assert len(mode) == 1 and mode[0] in outputs
args = ["--skipLibCheck", "--strict", "--pretty", "false", "--noEmit", "main.ts"]
report = {"flags":args, "sha256":{k:hashlib.sha256(b.read_bytes()).hexdigest() for k,b in bins.items()}, "widths":{}}
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "main.ts"
    widths = (1024, 4096, 8192, 16384) if mode == ["--shipping-public"] else (1024, 4096, 8192)
    for width in widths:
        subprocess.run([sys.executable, here.parent/"instantiated-symbol-reuse/handlers.py", p, str(width)], check=True)
        row = {"inputSha256": hashlib.sha256(p.read_bytes()).hexdigest(), "pairs":[]}
        for i in range(5):
            pair = {}
            for k in (bins if i % 2 else reversed(bins)):
                start = time.perf_counter_ns()
                r = subprocess.run([bins[k], *args], env=env, cwd=tmp, capture_output=True, check=True)
                pair[k] = (time.perf_counter_ns() - start) / 1e6
                assert not r.stdout and not r.stderr
            if i:
                row["pairs"].append(pair)
            else:
                row["warmup"] = pair
        report["widths"][width] = row
        print(width, {k:statistics.median(p[k] for p in row["pairs"]) for k in bins}, flush=True)
output = outputs[mode[0]]
(here/output).write_text(json.dumps(report, indent=2)+"\n")
