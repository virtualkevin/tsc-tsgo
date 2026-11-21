"""Separate factory initialization from allocations and GC assist on parser stacks."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import runpy

here = Path(__file__).resolve().parent
frontend = runpy.run_path(str(here.parent/'frontend-cpu-attribution/analyze.py'))
decode = runpy.run_path(str(here.parent/'call-resolution-partition/analyze.py'))['decode']
ref = json.loads((here.parent/'frontend-cpu-attribution/report.json').read_text())
report = {}
for project, baseline in ref.items():
    data = gzip.decompress((here.parent/'avx-opportunity-audit'/(project+'.raw.gz')).read_bytes())
    digest = hashlib.sha256(data).hexdigest()
    assert digest == baseline['rawSha256']
    buckets, allocations = Counter(), Counter()
    for ns, frames in decode(data.decode()):
        names = [f[0] for f in frames]
        if frontend['attribute'](names)[1] != 'AST construction':
            continue
        malloc = any('runtime.mallocgc' in f or f == 'runtime.growslice' for f in names)
        if malloc:
            index = next(i for i in range(len(names)-1,-1,-1) if 'runtime.mallocgc' in names[i] or names[i]=='runtime.growslice')
            caller = names[index+1] if index+1 < len(names) else '(root)'
            constructor = next((n.split('NodeFactory).',1)[1] for n in names if '/ast.(*NodeFactory).New' in n), '(other factory)')
            allocations[constructor+' / '+caller.split('[',1)[0]] += ns
            if any('gcAssistAlloc' in f for f in names):
                bucket = 'allocator including GC assist'
            elif any('memclr' in f for f in names):
                bucket = 'allocator including clearing'
            else:
                bucket = 'remaining allocator'
        elif any(f.endswith(('/ast.newNode','/ast.(*NodeFactory).newNode')) for f in names):
            bucket = 'shared node initialization'
        else:
            bucket = 'other factory work'
        buckets[bucket] += ns
    assert buckets.total() == baseline['parserCpuNs']['AST construction']
    report[project] = dict(rawSha256=digest, bucketsNs=dict(buckets), allocatorCallersNs=dict(allocations.most_common()))
    print(project, buckets)
(here/'cpu.json').write_text(json.dumps(report,indent=2)+'\n')
