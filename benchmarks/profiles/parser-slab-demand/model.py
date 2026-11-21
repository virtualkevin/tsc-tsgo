"""Compare typed page counts and payload capacities when a file starts with one mixed slab."""
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

here=Path(__file__).resolve().parent
inventory=json.loads((here/"inventory.json").read_text())
types=inventory["types"]
layout=json.loads((here/"layout.json").read_text())
assert [layout[t]["Bytes"] for t in types]==inventory["elementBytes"]
transitions=[{int(k):v for k,v in layout[t]["Next"].items()} for t in types]
sizes=inventory["elementBytes"]

@lru_cache(maxsize=None)
def pages(index, count, initial=0):
    # Initial storage belongs to the mixed slab. Count only additional backing arrays here.
    capacity=initial
    needed=count-initial
    records=0
    slots=0
    while needed>0:
        nxt=transitions[index][capacity]
        if nxt==capacity:
            remain=(needed+nxt-1)//nxt
            records+=remain
            slots+=remain*nxt
            break
        records+=1
        slots+=nxt
        needed-=nxt
        capacity=nxt
    return records, slots*sizes[index]

# Equal-capacity first pages isolate coallocation. Larger seeds also change growth.
kinds=["Identifier","NodeList","Token","StringLiteral","PropertyAccessExpression"]
small={t:transitions[types.index(t)][0] for t in kinds}
configs={"first pages":small,"larger first pages":dict(zip(kinds,[16,8,4,4,4]))}
for name, group in [
    ("common syntax", kinds+["ModifierList","VariableDeclaration","VariableDeclarationList","VariableStatement","CallExpression","ParameterDeclaration","Block","TypeReferenceNode","PropertyAssignment","BinaryExpression","ExpressionStatement"]),
    ("all typed arenas", types),
]:
    configs[name] = {t:transitions[types.index(t)][0] for t in group if t in types}
configs["weighted common syntax"] = configs["common syntax"] | configs["larger first pages"]
report={"scope":"Typed arena backings for observed per-file factory New calls only. Bytes use element size times actual capacity. Excludes allocator rounding after capacity selection, GC retention after file release and other parser allocations. No CPU or wall-time prediction.","configurations":configs,"projects":{}}
for name,p in inventory["projects"].items():
    raw=gzip.decompress((here/f"{name}.json.gz").read_bytes())
    assert hashlib.sha256(raw).hexdigest()==p["rawSha256"]
    rows=json.loads(raw)
    baseline=[0,0]
    for _,_,counts,_ in rows:
        for i,n in enumerate(counts):
            allocations,storage=pages(i,n)
            baseline[0]+=allocations
            baseline[1]+=storage
    project={"baselineAllocations":baseline[0],"baselineBytes":baseline[1],"models":[]}
    for nameOfConfig,config in configs.items():
        starts={types.index(t):c for t,c in config.items()}
        for cutoff in [0,1024,4096,16384]:
            deltaCount=deltaBytes=eligible=0
            for _,length,count,_ in rows:
                if length<cutoff: continue
                eligible+=1
                deltaCount+=1
                for i,c in starts.items():
                    before,b=pages(i,count[i])
                    after,a=pages(i,count[i],c)
                    deltaCount+=after-before
                    deltaBytes+=a+c*sizes[i]-b
            project["models"].append(dict(config=nameOfConfig,minFileBytes=cutoff,eligibleFiles=eligible,
                                          allocationDelta=deltaCount,payloadByteDelta=deltaBytes))
    report["projects"][name]=project
    print(name,baseline,project["models"][2],project["models"][6],flush=True)
(here/"model.json").write_text(json.dumps(report,indent=2)+"\n")
