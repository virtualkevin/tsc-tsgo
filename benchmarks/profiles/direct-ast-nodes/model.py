"""Estimate how many separately allocated, reachable nodes can fill small typed pages."""
import gzip
import hashlib
import json
from pathlib import Path

here=Path(__file__).resolve().parent
inventory=json.loads((here/"inventory.json").read_text())
report={}
for name,meta in inventory["projects"].items():
    raw=gzip.decompress((here/f"{name}.json.gz").read_bytes())
    assert hashlib.sha256(raw).hexdigest()==meta["sha256"]
    files=json.loads(raw)
    groups={}
    for t in inventory["types"]:
        counts=[row[1][t] for row in files if t in row[1]]
        if not counts:continue
        n=sum(counts)
        # Allocate a single object on first occurrence, then eight per page.
        blocks=sum((c-1+7)//8 for c in counts)
        groups[t]=dict(nodes=n,files=len(counts),singletonFiles=counts.count(1),
                       allocations=len(counts)+blocks,unusedSlots=len(counts)+8*blocks-n)
    report[name]=dict(files=len(files),byKind=dict(sorted(groups.items(),key=lambda p:-p[1]["nodes"])))
    top=list(report[name]["byKind"].items())[:5]
    print(name,[(k,v["nodes"],v["allocations"],v["unusedSlots"]) for k,v in top])
(here/"model.json").write_text(json.dumps(report,indent=2)+"\n")
