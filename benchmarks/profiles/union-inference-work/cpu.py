"""Partition CPU beneath the innermost inferToMultipleTypes by dispatch line."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
profiles = here.parent/"shipped-cpu-costs"
old = json.loads((profiles/"manifest.json").read_text())
report = {}
for project in ("sentry","vscode","typeorm","trpc"):
    path = profiles/f"{project}-cpu.pb.gz"
    expected = old["projects"][project]["profiles"]["cpu"]
    if project == "sentry":
        path = here.parent/"template-index-text/sentry-guard.pb.gz"
        expected = (path.parent/"profile-sha256.txt").read_text().split()[1]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", path], text=True)
    samples, locations = raw.split("Locations\n",1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        m = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)",line)
        if m:
            current = frames[int(m[1])] = []
            line = m[2]
        f = re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?",line)
        if f:
            current.append((f[1].split(".")[-1],int(f[3])))
    rows = Counter()
    objectSites = Counter()
    total = 0
    for ns,stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$",samples,re.M):
        ns = int(ns)
        total += ns
        calls = [f for i in stack.split() for f in frames[int(i)]]
        at = next((i for i, (f,_) in enumerate(calls) if f=="inferToMultipleTypes"),None)
        if at is None:
            continue
        focus = calls[at]
        step = next((f for f in reversed(calls[:at]) if f[0]=="inferFromTypes"), ("other",0))
        rows[f"{focus[1]} / {step[0]}:{step[1]}"] += ns
        if step == ("inferFromTypes",303):
            obj = next(((f,line) for f,line in reversed(calls[:at]) if f=="inferFromObjectTypes"),("invokeOnce",0))
            objectSites[obj[1]] += ns
    report[project] = dict(profileSha256=expected,totalCpuNs=total,multipleCpuNs=sum(rows.values()),sites=dict(rows.most_common()), objectSites=dict(objectSites.most_common()))
    print(project, sum(rows.values())/1e9, rows.most_common(5))
(here/"cpu.json").write_text(json.dumps(report, indent=2)+"\n")
