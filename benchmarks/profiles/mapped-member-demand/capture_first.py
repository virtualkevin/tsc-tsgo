import hashlib
import json
from pathlib import Path
import sys

here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects

binary=Path(sys.argv[1]).resolve()
out={"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"columns":["owners","symbols","symbolsWithoutNamedOrTypeAccess"],"projects":{}}
for name,commit,data in observed_projects(binary):
    assert data["Dropped"]==0
    buckets=[sum(b) for b in zip(*data["Cohorts"],strict=True)]
    sites=data["First"]
    assert sum(r[1] for r in sites.values())==sum(buckets)
    assert sum(r[2] for r in sites.values())==sum(n for i,n in enumerate(buckets) if i&3==0)
    assert sites.get("(no container exposure)",[0,0,0])[1]==sum(buckets[:4])
    ordered=dict(sorted(sites.items(),key=lambda x:(-x[1][1],x[0])))
    out["projects"][name]={"commit":commit,"byFirstExposure":ordered}
    print(name,list(ordered.items())[:3],flush=True)
(here/"first-exposure.json").write_text(json.dumps(out,indent=2)+"\n")
