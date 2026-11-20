"""Attribute CPU samples that have any pointer-link probe on their stack."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
pprof, control, advised = sys.argv[1:]
report = {}
for mode, binary in (("control",control),("advised",advised)):
    profile = here/(mode+"-cpu.pb.gz")
    raw = subprocess.check_output([pprof,"-raw",binary,profile],text=True)
    samples, locations = raw.split("Locations\n",1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        m = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?:\s+M=\d+)?\s+(.*)",line)
        if m:
            addr = int(m[1])
            frames[addr] = []
            line = m[2]
        m = re.match(r"(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+(?:\(.*\))?)?$",line.strip())
        if m:
            frames[addr].append(m[1])
    callers = Counter()
    total = flat = 0
    def is_probe(name):
        return name.startswith("github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[") and name.endswith("]).slot")
    prefix = "github.com/microsoft/typescript-go/internal/checker."
    for line in samples.splitlines():
        m = re.match(r"^\s+\d+\s+(\d+):\s*(.*)$",line)
        if m:
            ns = int(m[1])
            total += ns
            stack = [f for addr in map(int,m[2].split()) for f in frames[addr]]
            assert stack
            if any(map(is_probe,stack)):
                flat += ns if is_probe(stack[0]) else 0
                caller = next((f.removeprefix(prefix) for f in stack if f.startswith(prefix)), "outside checker")
                callers[caller] += ns
    assert 0 < flat <= sum(callers.values()) <= total
    report[mode] = dict(profileSha256=hashlib.sha256(profile.read_bytes()).hexdigest(), totalCpuNs=total,
                        slotInclusiveNs=sum(callers.values()), slotFlatNs=flat, callersNs=dict(callers.most_common()))
(here/"budget.json").write_text(json.dumps(report,indent=2)+"\n")
