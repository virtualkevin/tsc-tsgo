"""Attribute CPU under program construction and file-loader workers in retained profiles."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

here = Path(__file__).resolve().parent
prior = here.parent / 'avx-opportunity-audit'
anchor = re.compile(r'/compiler\.(?:NewProgram$|\(\*(?:filesParser|fileLoader|parseTask|projectReferenceParser)\)\.)')
host = '/compiler.(*compilerHost).GetSourceFile'
parser = '/parser.ParseSourceFile'
rules = [
    ('child parent assignment', ('overrideParentInImmediateChildren','setParentFromContext')),
    ('identifier interning', ('internIdentifier',)),
    ('module reference collection', ('/parser.collectExternalModuleReferences','/parser.(*externalModule')),
    ('scanner', ('/scanner.',)),
    ('AST construction', ('/ast.(*NodeFactory).',)),
]
def attribute(functions):
    if not any(anchor.search(f) for f in functions):
        return 'outside anchored stacks', None
    if any(host in f for f in functions) and any(parser in f for f in functions):
        for name, parts in rules:
            if any(part in f for f in functions for part in parts):
                return 'source parsing', name
        return 'source parsing', 'remaining parser stack'
    if any('/module.' in f or '/packagejson.' in f for f in functions):
        return 'module or package resolution', None
    if any(host in f for f in functions):
        return 'source host outside parser', None
    return 'other anchored work', None

def analyze(raw):
    samples, locations = raw.split('Locations\n',1)
    functions = {}
    current = None
    for line in locations.split('Mappings\n')[0].splitlines():
        match = re.match(r'^\s*(\d+):\s+0x[\da-f]+(?:\s+M=\d+)?\s+(.*)',line)
        if match:
            current = int(match[1])
            functions[current] = []
            line = match[2]
        f = re.match(r'(.+?)\s+\S+:\d+:\d+(?:\s+s=\d+(?:\(.*\))?)?$',line.strip())
        if f and current is not None:
            functions[current].append(f[1])
    phases, parsing = Counter(), Counter()
    constructors, allocation = Counter(), Counter()
    for line in samples.splitlines():
        m = re.match(r'^\s+\d+\s+(\d+):\s*(.*)$',line)
        if not m:
            continue
        ns = int(m[1])
        stack = []
        for addr in map(int,m[2].split()):
            assert functions[addr]
            stack.extend(functions[addr])
        phase, component = attribute(stack)
        phases[phase] += ns
        if component:
            parsing[component] += ns
        if component == 'AST construction':
            name = next((f.split('NodeFactory).', 1)[1] for f in stack if '/ast.(*NodeFactory).New' in f), 'other factory')
            constructors[name] += ns
            alloc = any('runtime.mallocgc' in f or f == 'runtime.growslice' for f in stack)
            allocation['allocator on stack' if alloc else 'other construction'] += ns
    assert sum(parsing.values()) == phases['source parsing'] > 0
    assert sum(constructors.values()) == sum(allocation.values()) == parsing['AST construction']
    return dict(phaseCpuNs=phases, parserCpuNs=parsing, constructorCpuNs=constructors, constructorAllocationCpuNs=allocation)

if __name__ == '__main__':
    report = {}
    for row in json.loads((prior/'report.json').read_text())['projects']:
        name = row['workload']
        raw = gzip.decompress((prior/(name+'.raw.gz')).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == row['rawSha256']
        data = analyze(raw.decode())
        assert sum(data['phaseCpuNs'].values()) == row['totalCpuNs']
        report[name] = dict(rawSha256=row['rawSha256'], **data)
        print(name, data['constructorAllocationCpuNs'], data['constructorCpuNs'].most_common(3), flush=True)
    (here/'report.json').write_text(json.dumps(report,indent=2)+'\n')
