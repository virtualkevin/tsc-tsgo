"""Count inspected slots on a synthetic table at two controlled occupancies."""
import json
from pathlib import Path
from random import Random
from statistics import mean

capacity = 1 << 16
rng = Random(360821)
home = [rng.randrange(capacity) for _ in range(capacity*2)]
def probe(table, key, grouped):
    start = home[key]
    step = 4
    while True:
        for offset in range(4):
            slot = (start+offset) & (capacity-1)
            yield slot
            if table[slot] == key or table[slot] is None:
                return
        start = (start+step) & (capacity-1)
        if grouped:
            step += 4

report = {}
for size in (capacity//2,3*capacity//4):
    for grouped in (False,True):
        table = [None]*capacity
        for key in range(size):
            for slot in probe(table,key,grouped):
                pass
            assert table[slot] is None
            table[slot] = key
        summaries = {}
        for label, keys in (("hits",range(size)), ("misses",range(capacity,2*capacity))):
            counts=[]
            for key in keys:
                path=list(probe(table,key,grouped))
                assert table[path[-1]] == (key if label=="hits" else None)
                counts.append(len(path))
            counts.sort()
            summaries[label]=dict(mean=mean(counts),p99=counts[(99*len(counts)-1)//100],maximum=max(counts))
        report[f"{size}/{capacity} {'grouped' if grouped else 'linear'}"]=summaries
(Path(__file__).resolve().parent/"probe-counts.json").write_text(json.dumps(report,indent=2)+"\n")
