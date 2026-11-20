"""Observe Linux huge-page advice on Go heap VMAs during untimed cold checks."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
binary = Path(sys.argv[1]).resolve()
def read_heap(pid):
    total = advised = huge = 0
    in_heap = False
    for line in Path(f"/proc/{pid}/smaps").read_text().splitlines():
        if re.match(r"^[0-9a-f]+-[0-9a-f]+ ", line):
            in_heap = line.endswith("[anon: Go: heap]")
            size = 0
        elif in_heap:
            if line.startswith("Size:"):
                size = int(line.split()[1])
                total += size
            elif line.startswith("AnonHugePages:"):
                huge += int(line.split()[1])
            elif line.startswith("VmFlags:") and "hg" in line.split()[1:]:
                advised += size
    return total, advised, huge

report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"projects":{}}
for group in ("small","large"):
    ref = here.parent/"heap-page-confirmation"/(group+".json.gz")
    run = json.loads(gzip.decompress(ref.read_bytes()))
    env = {k:v for k,v in os.environ.items() if k not in run["environment"]["unsetEnvironment"]
           and not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
    env.update(run["environment"]["compilerEnvironment"], GODEBUG="decoratemappings=1")
    for p in run["projects"]:
        cwd = Path(p["cwd"])
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip() == p["commit"]
        for f in p["preflight"]["candidate"]["inputs"]:
            assert hashlib.sha256((cwd/f["file"]).read_bytes()).hexdigest() == f["sha256"]
        with subprocess.Popen([binary,*p["compilerArgs"]["candidate"]],cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as proc:
            observations = []
            while proc.poll() is None:
                try:
                    observations.append(read_heap(proc.pid))
                except (FileNotFoundError, ProcessLookupError):
                    break
                time.sleep(0.15)
            stdout, stderr = proc.communicate()
            assert proc.returncode == 0 and not stdout and not stderr
        peaks = list(map(max,zip(*observations)))
        assert peaks[0] > 0
        row = dict(zip(("peakHeapMappedKiB","peakAdvisedKiB","peakHugeKiB"),peaks))
        row["samples"] = len(observations)
        report["projects"][p["name"]] = row
        print(p["name"],row,flush=True)
(here/"pages.json").write_text(json.dumps(report,indent=2)+"\n")
