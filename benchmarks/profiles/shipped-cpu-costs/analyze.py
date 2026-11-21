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
    "checker": ("typescript-go/internal/checker.",),
    "binder": ("typescript-go/internal/binder.",),
    "parseScan": ("typescript-go/internal/parser.", "typescript-go/internal/scanner."),
    "relations": ("internal/checker.(*Relater).isRelatedToEx",),
    "instantiation": ("internal/checker.(*Checker).instantiateTypeWithAlias",),
    "symbolType": ("internal/checker.(*Checker).getTypeOfSymbol",),
    "allocation": ("runtime.mallocgc",),
    "unionNormalize": ("internal/checker.(*Checker).getUnionTypeWorker",),
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
    cum,only,leaf,callers = Counter(),Counter(),Counter(),Counter()
    for ns,stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$",samples,re.M):
        weight = int(ns)
        entries = [frame for i in stack.split() for frame in frames[int(i)]]
        if not stack.split() or not frames[int(stack.split()[0])]:
            entries.insert(0, ("<unsymbolized>", "", 0))
        hit = [cat for cat,terms in categories.items() if any(any(t in func for t in terms) for func,_,_ in entries)]
        only["+".join(hit) or "other"] += weight
        for cat in hit:
            cum[cat] += weight
        if "goMap" in hit:
            # Innermost sampled map operation, then the nearest compiler caller.
            start = next(i for i,(f,_,_) in enumerate(entries) if any(t in f for t in categories["goMap"]))
            source = next(((file,line) for _,file,line in entries[start+1:]
                           if "typescript-go/" in file), None)
            key = ("%s:%d" % source).split("typescript-go/")[-1] if source else "<runtime or other>"
            callers[key] += weight
        _,file,line = entries[0]
        if file.endswith("/pointerlinkstore.go"):
            leaf[line] += weight
    phases = Counter()
    for bucket,weight in only.items():
        families = set(bucket.split("+"))
        phase = next((x for x in ("gcMark","checker","binder","parseScan") if x in families), "other")
        phases[phase] += weight
    total = only.total()
    assert phases.total() == total
    assert total > 0 and callers.total() == cum["goMap"]
    report["projects"][name] = dict(totalCpuNs=total,exclusivePhasesNs=phases,inclusiveNs=cum,exclusiveNs=only,pointerLinkLeafLineNs=leaf,goMapCallerNs=dict(callers.most_common()))
    print(name, {k: round(v*100/total,2) for k,v in cum.items()}, leaf.most_common(4))
(here/"costs.json").write_text(json.dumps(report,indent=2)+"\n")
