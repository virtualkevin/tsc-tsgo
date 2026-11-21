"""Partition four retained Go CPU profiles at the outermost union worker."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

here = Path(__file__).resolve().parent
archive = here.parent / "avx-opportunity-audit"
report = {}
for project in json.loads((archive / "report.json").read_text())["projects"]:
    name = project["workload"]
    raw = gzip.decompress((archive / (name + ".raw.gz")).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == project["rawSha256"]
    samples, locations = raw.decode().split("Locations\n", 1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        match = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?:\s+M=\d+)?\s*(.*)", line)
        if match:
            addr = int(match[1])
            frames[addr] = []
            line = match[2]
        match = re.match(r"(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+(?:\(.*\))?)?$", line.strip())
        if match:
            frames[addr].append(match[1])
    total = 0
    buckets = Counter()
    subtype_children = Counter()
    worker = "github.com/microsoft/typescript-go/internal/checker.(*Checker).getUnionTypeWorker"
    for line in samples.splitlines():
        match = re.match(r"^\s+\d+\s+(\d+):\s*(.*)$", line)
        if not match:
            continue
        ns = int(match[1])
        total += ns
        stack = [f for a in map(int, match[2].split()) for f in frames[a]]
        for i in range(len(stack)-1, -1, -1):
            if stack[i] == worker:
                callee = stack[i-1] if i else "worker self"
                child = callee.removeprefix("github.com/microsoft/typescript-go/internal/")
                buckets[child] += ns
                if child == "checker.(*Checker).removeSubtypes":
                    nested = stack[i-2] if i >= 2 else "removeSubtypes self"
                    subtype_children[nested.removeprefix("github.com/microsoft/typescript-go/internal/")] += ns
                break
    assert total == project["totalCpuNs"] and buckets
    report[name] = dict(rawSha256=project["rawSha256"], totalCpuNs=total,
                        workerCpuNs=sum(buckets.values()), childrenNs=dict(buckets.most_common()),
                        subtypeChildrenNs=dict(subtype_children.most_common()))
(here / "cpu.json").write_text(json.dumps(report,indent=2) + "\n")
