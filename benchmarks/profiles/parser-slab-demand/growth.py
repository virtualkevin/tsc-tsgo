"""Fit per-kind lazy arena growth on three workloads and evaluate on the fourth."""
from collections import Counter
from functools import lru_cache
import gzip
import json
from pathlib import Path

here=Path(__file__).resolve().parent
inventory=json.loads((here/"inventory.json").read_text())
models=json.loads((here/"model.json").read_text())
layout=json.loads((here/"layout.json").read_text())
kinds=inventory["types"]
projects=list(inventory["projects"])
hist={}
for p in projects:
    rows=json.loads(gzip.decompress((here/f"{p}.json.gz").read_bytes()))
    hist[p]=[Counter(r[2][i] for r in rows if r[2][i]) for i in range(len(kinds))]
policies=[(a,b) for a in (2,4,8,16,32) for b in (16,32,64,128,256) if a<=b]
base=(2,256)
cost={}
for i,k in enumerate(kinds):
    size=layout[k]["Bytes"]
    grow={int(key):n for key,n in layout[k]["Next"].items()}
    rounded={n:grow[n//2 if n>2 else 0] for n in (2,4,8,16,32,64,128)}
    rounded[256]=grow[max(grow)]
    for first,limit in policies:
        # Ask the pinned Go allocator for its rounded capacity after requesting N.
        # The lookup of grow[N/2] measured exactly slices.Grow(nil,N).
        cap=rounded[first]
        slots=[cap]
        while cap<limit:
            cap=grow[cap] if 2*cap<=limit else rounded[limit]
            slots.append(cap)
        repeat=rounded[limit]
        ends=[]
        total=0
        for n in slots:
            total+=n
            ends.append(total)
        @lru_cache(maxsize=None)
        def usage(count):
            for pages,total in enumerate(ends,1):
                if count<=total:return pages,total*size
            extra=(count-total+repeat-1)//repeat
            return len(ends)+extra,(total+extra*repeat)*size
        for p in projects:
            count=mem=0
            for n,freq in hist[p][i].items():
                pages,storage=usage(n)
                count+=pages*freq
                mem+=storage*freq
            cost[p,k,first,limit]=(count,mem)
        usage.cache_clear()
def solve(training):
    policy={}
    for k in kinds:
        eligible=[]
        for rule in policies:
            delta=[tuple(a-b for a,b in zip(cost[p,k,*rule],cost[p,k,*base],strict=True)) for p in training]
            if all(c<=0 and b<=0 for c,b in delta):
                eligible.append((sum(c for c,b in delta),sum(b for c,b in delta),rule!=base,rule))
        policy[k]=min(eligible)[-1]
    return policy
report={}
for held in [*projects,None]:
    training=[p for p in projects if p!=held]
    policy=solve(training)
    rows={}
    for p in projects:
        counts,storage=map(sum,zip(*(cost[p,k,*policy[k]] for k in kinds)))
        oldCounts,oldBytes=map(sum,zip(*(cost[p,k,*base] for k in kinds)))
        assert (oldCounts,oldBytes)==(models["projects"][p]["baselineAllocations"],models["projects"][p]["baselineBytes"])
        rows[p]=dict(allocationDelta=counts-oldCounts,payloadByteDelta=storage-oldBytes)
    report[held or "all projects"]=dict(training=training,policy={k:v for k,v in policy.items() if v!=base},projects=rows)
    print(held or "all projects",len(report[held or "all projects"]["policy"]),rows[held] if held else rows)
(here/"growth.json").write_text(json.dumps(report,indent=2)+"\n")
