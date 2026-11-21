"""Partition CPU beneath the outermost getTypeOfInstantiatedSymbol by its direct callee."""
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
    worker = Counter()
    total = 0
    for ns,stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$",samples,re.M):
        ns = int(ns)
        total += ns
        calls = [f for i in stack.split() for f in frames[int(i)]]
        index = next((i for i in range(len(calls)-1,-1,-1) if calls[i][0]=="getTypeOfInstantiatedSymbol"),None)
        if index is None:
            continue
        child = calls[index-1][0] if index else "self"
        rows[child] += ns
        if child == "instantiateType":
            i = next((i for i in range(index-1,-1,-1) if calls[i][0]=="instantiateTypeWorker"), None)
            work = "outsideWorker" if i is None else (calls[i-1][0] if i else "self")
            worker[work] += ns
    report[project] = dict(profileSha256=expected, totalCpuNs=total,
                           resolverCpuNs=sum(rows.values()), childrenNs=dict(rows.most_common()), instantiationWorkerChildrenNs=dict(worker.most_common()))
    print(project, rows.most_common(4))
(here/"cpu.json").write_text(json.dumps(report, indent=2)+"\n")
