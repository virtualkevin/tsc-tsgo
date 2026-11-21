"""Attribute retained symbol-read samples to dispatch and immediate table probes."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

here = Path(__file__).resolve().parent
archive = here.parent / "avx-opportunity-audit"
prefix = "github.com/microsoft/typescript-go/internal/"
checker = "checker.(*Checker)."
entry = checker + "getTypeOfSymbol"
getters = {checker + n for n in ("getTypeOfSymbolWithDeferredType","getTypeOfInstantiatedSymbol",
    "getTypeOfMappedSymbol","getTypeOfReverseMappedSymbol","getTypeOfAccessors",
    "getTypeOfVariableOrParameterOrProperty","getTypeOfFuncClassEnumModule")}
def probe(frame):
    return (frame.startswith("core.(*PointerLinkStore[") and frame.endswith((".Get",".slot"))
            or frame.startswith("core.pointerLinkHash["))

report = {}
for p in json.loads((archive/"report.json").read_text())["projects"]:
    name=p["workload"]
    raw=gzip.decompress((archive/(name+".raw.gz")).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==p["rawSha256"]
    samples,locations=raw.decode().split("Locations\n",1)
    frames={}
    for line in locations.split("Mappings\n")[0].splitlines():
        m=re.match(r"^\s*(\d+):\s+0x[\da-f]+(?:\s+M=\d+)?\s*(.*)",line)
        if m:
            addr=int(m[1]); frames[addr]=[]; line=m[2]
        m=re.match(r"(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+(?:\(.*\))?)?$",line.strip())
        if m:
            frames[addr].append(m[1].removeprefix(prefix))
    totals=Counter()
    callers=Counter()
    for line in samples.splitlines():
        m=re.match(r"^\s+\d+\s+(\d+):\s*(.*)$",line)
        if not m:continue
        ns=int(m[1]);totals["all"]+=ns
        stack=[f for a in map(int,m[2].split()) for f in frames[a]]
        # A slot stack measures probing; a Get stack alone can include allocation.
        slot=next((i for i,f in enumerate(stack)
                   if f.startswith("core.(*PointerLinkStore[") and f.endswith(".slot")),None)
        if slot is not None:
            totals["allPointerTableSlots"]+=ns
            caller=next((f for f in stack[slot+1:] if f.startswith("checker.")),"outside checker or truncated")
            callers[caller]+=ns
        if entry not in stack:continue
        totals["underSymbolRead"]+=ns
        # Use the innermost read in a recursive stack. Exclude descendants of
        # semantic workers, table growth, and other non-probe functions.
        path=stack[:stack.index(entry)][::-1]
        if not path:totals["dispatchSelf"]+=ns
        elif path[0] in getters:
            if len(path)==1:totals["getterSelf"]+=ns
            elif all(probe(f) for f in path[1:]):totals["directTableProbe"]+=ns
    assert totals["all"]==p["totalCpuNs"] and totals["underSymbolRead"]
    report[name]=dict(rawSha256=p["rawSha256"],cpuNs=totals,topSlotCallersNs=dict(callers.most_common(10)))
(here/"cpu.json").write_text(json.dumps(report,indent=2)+"\n")
