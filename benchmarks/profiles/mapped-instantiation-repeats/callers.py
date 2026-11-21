"""Rank callers of the outermost type-instantiation entry in size-aware Sentry."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys

here=Path(__file__).resolve().parent
profile=here.parent/"grouped-pointer-probes/advised-cpu.pb.gz"
binary=here.parents[2]/"packages/tsc-go/dist/tsc-go-large-heap-pages"
raw=subprocess.check_output([sys.argv[1],"-raw",binary,profile],text=True)
samples,locations=raw.split("Locations\n",1)
frames={}
for line in locations.split("Mappings\n")[0].splitlines():
    m=re.match(r"^\s*(\d+):\s+0x[\da-f]+(?:\s+M=\d+)?\s+(.*)",line)
    if m:
        addr=int(m[1]); frames[addr]=[]; line=m[2]
    m=re.match(r"(.+?)\s+(\S+):(\d+):\d+(?:\s+s=\d+(?:\(.*\))?)?$",line.strip())
    if m:
        frames[addr].append((m[1],m[2],int(m[3])))
prefix="github.com/microsoft/typescript-go/internal/"
entries={prefix+"checker.(*Checker)."+n for n in ("instantiateType","instantiateTypeWithAlias","instantiateTypeWorker")}
counts=Counter()
total=0
for line in samples.splitlines():
    m=re.match(r"^\s+\d+\s+(\d+):\s*(.*)$",line)
    if not m: continue
    ns=int(m[1]); total+=ns
    stack=[f for a in map(int,m[2].split()) for f in frames[a]]
    outer=next((i for i in range(len(stack)-1,-1,-1) if stack[i][0] in entries),None)
    if outer is not None:
        if outer+1==len(stack):
            caller="truncated stack"
        else:
            name,path,lineno=stack[outer+1]
            caller=f"{name.removeprefix(prefix)} {path.removeprefix(prefix)}:{lineno}"
        counts[caller]+=ns
assert total==json.loads((here/"cpu.json").read_text())["sentry-size-aware"]["totalCpuNs"]
report=dict(totalCpuNs=total,instantiationCpuNs=sum(counts.values()),callersNs=dict(counts.most_common()))
(here/"callers.json").write_text(json.dumps(report,indent=2)+"\n")
print(round(100*sum(counts.values())/total,2),counts.most_common(6))
