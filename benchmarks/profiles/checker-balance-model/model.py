"""Replay static four-worker ownership with fixed observed callback costs."""
import gzip
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
source = here.parent/"contiguous-checker-locality/file-cost-results"
report = {}
for run in json.loads((source/"report.json").read_text())["runs"]:
    if run["scheduler"] != "default":
        continue
    raw = gzip.decompress((source/(run["project"]+"-default.jsonl.gz")).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == run["logSha256"]
    batches = raw.splitlines()
    assert len(batches) == 1
    files = json.loads(batches[0])
    assert len({r["File"] for r in files}) == len(files)
    def busiest(owners):
        loads = [0]*4
        for owner, row in zip(owners,files,strict=True):
            loads[owner] += row["ElapsedNS"]
        return max(loads)
    actual = [r["Checker"] for r in files]
    assert set(actual) == set(range(4))
    lower = max(sum(r["ElapsedNS"] for r in files)/4, max(r["ElapsedNS"] for r in files))
    baseline = busiest(actual)
    result = {"sourceSha256":run["logSha256"],"observedBusiestNs":baseline,
              "fixedWorkLowerBoundNs":lower,"idealSpeedupCeiling":baseline/lower,"models":{}}
    for field in ("Bytes","Nodes","Symbols","ElapsedNS"):
        loads = [0]*4
        owners = actual.copy()
        eligible = [i for i,r in enumerate(files) if r["Checked"]]
        for i in sorted(eligible,key=lambda i:-files[i][field]):
            worker = min(range(4),key=loads.__getitem__)
            owners[i] = worker
            loads[worker] += max(1,files[i][field])
        result["models"][field] = baseline/busiest(owners)
    report[run["project"]] = result
    print(run["project"], result["idealSpeedupCeiling"],result["models"])
(here/"report.json").write_text(json.dumps(report,indent=2)+"\n")
