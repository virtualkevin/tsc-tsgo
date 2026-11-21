"""Run the probe on the same four project inputs as the live symbol experiment."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
probe = Path(sys.argv[1]).resolve()
control = json.loads((here.parent/"live-symbol-slots/counts.json").read_text())
report = {"controlSha256": control["binarySha256"]["control"], "binarySha256": hashlib.sha256(probe.read_bytes()).hexdigest(), "projects": {}}
for group in ("small", "large"):
    frozen = json.loads((root/f"benchmarks/results/native-project-inlining/{group}.json").read_text())
    env = {k:v for k,v in os.environ.items() if k not in frozen["environment"]["unsetEnvironment"]
           and not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
    env.update(frozen["environment"]["compilerEnvironment"])
    for p in frozen["projects"]:
        cwd = Path(p["cwd"])
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd, text=True).strip()
        assert commit == p["commit"]
        for item in p["preflight"]["candidate"]["inputs"]:
            assert hashlib.sha256((cwd/item["file"]).read_bytes()).hexdigest() == item["sha256"]
        run = subprocess.run([probe, *p["args"], "--extendedDiagnostics"], cwd=cwd, env=env,
                             timeout=400, capture_output=True, text=True, check=True)
        counts = json.loads(run.stderr)
        assert 0 < counts["Files"] <= len(p["preflight"]["candidate"]["inputs"])
        assert 0 < counts["RequestedTypeNodes"] <= counts["TypeNodes"]
        assert 0 <= counts["NoWorkerRequestSpanBytes"] <= counts["TypeSpanBytes"] <= counts["FileBytes"]
        work = dict(re.findall(r"^(Files|Lines|Identifiers|Types|Symbols|Instantiations):\s*(\d+)\s*$", run.stdout, re.M))
        assert len(work) == 6 and not re.search(r"error TS\d+", run.stdout)
        work = {k:int(v) for k,v in work.items()}
        original = control["projects"][p["name"]]
        assert original["commit"] == commit
        diff = {k:[v,work[k]] for k,v in original["work"]["control"].items() if v != work[k]}
        assert not diff or (p["name"] == "typeorm" and set(diff) == {"Symbols"}), diff
        report["projects"][p["name"]] = dict(commit=commit, counts=counts, work=work, differences=diff)
        print(p["name"], counts, flush=True)
(here/"results.json").write_text(json.dumps(report, indent=2)+"\n")
