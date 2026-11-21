"""Attribute full CPU stacks and leaf instructions from verified production profiles."""
from collections import Counter
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
manifest = json.loads((here / "manifest.json").read_text())
categories = {
    "gcMark": ("runtime.gcDrain", "runtime.gcAssistAlloc", "runtime.gcBgMarkWorker", "runtime.scanObject"),
    "goMap": ("internal/runtime/maps.", "runtime.mapaccess", "runtime.mapassign"),
    "pointerLinks": ("internal/core.(*PointerLinkStore[", "internal/core.pointerLinkHash["),
}
report = {"families":categories,"projects":{}}
for name,p in manifest["projects"].items():
    path = here / f"{name}-cpu.pb.gz"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == p["profiles"]["cpu"]
    raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
    samples,locations = raw.split("Locations\n",1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        m = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)",line)
        if m:
            key = int(m[1])
            frames[key] = []
            line = m[2]
        f = re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?",line)
        if f:
            frames[key].append((f[1],f[2],int(f[3])))
    cum,only,leaf = Counter(),Counter(),Counter()
    for ns,stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$",samples,re.M):
        weight = int(ns)
        entries = [frame for i in stack.split() for frame in frames[int(i)]]
        if not stack.split() or not frames[int(stack.split()[0])]:
            entries.insert(0, ("<unsymbolized>", "", 0))
        hit = [cat for cat,terms in categories.items() if any(any(t in func for t in terms) for func,_,_ in entries)]
        only["+".join(hit) or "other"] += weight
        for cat in hit:
            cum[cat] += weight
        _,file,line = entries[0]
        if file.endswith("/pointerlinkstore.go"):
            leaf[line] += weight
    total = only.total()
    assert total > 0
    report["projects"][name] = dict(totalCpuNs=total,inclusiveNs=cum,exclusiveNs=only,pointerLinkLeafLineNs=leaf)
    print(name, {k: round(v*100/total,2) for k,v in cum.items()}, leaf.most_common(4))
(here/"costs.json").write_text(json.dumps(report,indent=2)+"\n")
