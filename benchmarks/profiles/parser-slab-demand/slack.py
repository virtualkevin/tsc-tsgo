"""Measure unused typed capacity by kind, including the partially filled final page."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

here=Path(__file__).resolve().parent
inventory=json.loads((here/"inventory.json").read_text())
model=json.loads((here/"model.json").read_text())
layout=json.loads((here/"layout.json").read_text())
report={}
for project,info in inventory["projects"].items():
    raw=gzip.decompress((here/f"{project}.json.gz").read_bytes())
    assert hashlib.sha256(raw).hexdigest()==info["rawSha256"]
    demand=Counter()
    backing=Counter()
    inputGroups={}
    for path,_,counts,final in json.loads(raw):
        group="other parsed file" if not final else ("declaration" if path.endswith((".d.ts",".d.cts",".d.mts")) else "source")
        bucket=inputGroups.setdefault(group,{"usedBytes":0,"capacityBytes":0})
        for kind,n in zip(inventory["types"],counts,strict=True):
            if not n:continue
            size=layout[kind]["Bytes"]
            demand[kind]+=n*size
            bucket["usedBytes"]+=n*size
            allocated=last=0
            while allocated<n:
                nxt=layout[kind]["Next"][str(last)]
                if last==nxt:
                    allocated+=((n-allocated+nxt-1)//nxt)*nxt
                    break
                allocated+=nxt
                last=nxt
            backing[kind]+=allocated*size
            bucket["capacityBytes"]+=allocated*size
    assert backing.total()==model["projects"][project]["baselineBytes"]
    unused=backing-demand
    report[project]={"usedBytes":demand.total(),"capacityBytes":backing.total(),"unusedBytes":unused.total(),
                     "inputGroups":inputGroups,"unusedBytesByKind":dict(unused.most_common())}
    print(project,round(100*unused.total()/backing.total(),1),unused.most_common(3))
(here/"slack.json").write_text(json.dumps(report,indent=2)+"\n")
