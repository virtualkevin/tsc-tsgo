"""Summarize session-cgroup CPU between the harness's before/after sample points."""
import gzip
import json
from pathlib import Path
from statistics import median

here = Path(__file__).resolve().parent
result = {}
for group in ("small", "large"):
    run = json.loads(gzip.decompress((here / (group+".json.gz")).read_bytes()))
    for p in run["projects"]:
        summary = {}
        for mode, key in (("advised", "baseline"), ("control", "candidate")):
            rows = []
            for pair in p["pairs"]:
                sample = pair["cgroupCpu"][key]
                before, after = (sample[k]["ancestors"][0] for k in ("before","after"))
                assert before["path"] == after["path"] and not before["errors"] and not after["errors"]
                row = {k: (int(after["cpuStat"][k]) - int(before["cpuStat"][k])) / 1e6
                       for k in ("user_usec","system_usec","usage_usec")}
                assert row["user_usec"] >= 0 and row["system_usec"] >= 0
                rows.append(row)
            summary[mode] = {k.removesuffix("_usec")+"Seconds": median(r[k] for r in rows) for k in rows[0]}
        result[p["name"]] = summary
(here/"cgroup-cpu.json").write_text(json.dumps(result,indent=2)+"\n")
