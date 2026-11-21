"""Attribute Sentry allocation samples and CPU to the anonymous-object instantiation path."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
manifest=json.loads((here/"profiles.json").read_text())
report={}
for name,entry in manifest["binaries"].items():
    profile={}
    for kind in ("cpu","mem"):
        path=here/f"sentry-{name}-{kind}.pb.gz"
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry[kind]
        raw=subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
        samples,locations=raw.split("Locations\n",1)
        frames={}
        for line in locations.split("Mappings\n")[0].splitlines():
            loc=re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)",line)
            if loc:
                frames[int(loc[1])]=current=[]
                line=loc[2]
            f=re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?",line)
            if f:
                current.append(f[1].split(".")[-1])
        byChild={}
        total=[0,0]
        for match in re.finditer(r"^\s*(\d+(?:\s+\d+)+):\s*([\d ]+)$",samples,re.M):
            values=list(map(int,match[1].split()))
            # First two fields are samples and nanoseconds (CPU) or estimated objects and bytes (heap).
            for i,x in enumerate(values[:2]):
                total[i]+=x
            stack=[f for n in match[2].split() for f in frames[int(n)]]
            pos=next((i for i in range(len(stack)-1,-1,-1) if stack[i]=="getObjectTypeInstantiation"),None)
            if pos is None:
                continue
            row=byChild.setdefault(stack[pos-1] if pos else "self",[0,0])
            for i,x in enumerate(values[:2]):
                row[i]+=x
        assert total[1] and byChild
        profile[kind]={"total":total,"objectInstantiationInclusive":[sum(p[i] for p in byChild.values()) for i in (0,1)],
                       "byImmediateCallee":dict(sorted(byChild.items(),key=lambda kv:-kv[1][1]))}
    report[name]=profile
(here/"attribution.json").write_text(json.dumps(report,indent=2)+"\n")
for k,v in report.items():
    print(k,[(n,v[n]["objectInstantiationInclusive"],v[n]["total"]) for n in ("mem","cpu")])
