"""Independent raw readback and descriptive analysis; no compiler promotion gate."""
import hashlib
import json
from pathlib import Path
import re
import statistics

p = Path(__file__).resolve().parent
sha = lambda f: hashlib.sha256(Path(f).read_bytes()).hexdigest()
c = json.loads((p / 'capture.json').read_text())
v = json.loads((p / 'validation.json').read_text())
cfg = json.loads((p / 'config.json').read_text())
assert c['status'] == v['status'] == 'passed'
for field, file in [('configSha256', 'config.json'), ('validationSha256', 'validation.json'), ('controllerSha256', 'capture.py')]:
    assert c[field] == sha(p / file)
assert v['controllerSha256'] == sha(p / 'validate.py')
assert v['overlaySha256'] == sha(p / 'overlay.json')
assert c['sources'] == v['sources']
for file, digest in c['sources'].items():
    assert sha(file) == digest
assert sha(v['build']['binary']) == c['binarySha256'] == v['build']['binarySha256']
assert sha(v['build']['command'][0]) == v['build']['toolchainSha256']
assert [r['mode'] for r in v['runs']] == ['normal', 'race', 'checkptr']
for run in v['runs']:
    assert run['ok'] and run['exitCode'] == 0
    for stream in ['stdout', 'stderr']:
        assert sha(p / (run['mode'] + '.' + stream)) == run[stream + 'Sha256']
    events = [json.loads(line) for line in (p / (run['mode'] + '.stdout')).read_text().splitlines()]
    passes = [e['Test'] for e in events if e.get('Action') == 'pass' and 'Test' in e]
    assert passes == run['passed'] and len(set(passes)) == 7
    assert not any(e.get('Action') in ('fail', 'skip', 'build-fail') for e in events)
expected = []
for kind, cases, pairs in [('benchmark', cfg['operations'], 9), ('retention', cfg['shapes'], 5)]:
    for n in cfg['sizes']:
        for case in cases:
            for pair in range(pairs):
                for side in (['pointer', 'compact'] if pair % 2 == 0 else ['compact', 'pointer']):
                    expected.append((kind, case, n, pair, side))
assert len(expected) == len(c['observations']) == 148
files = set()
for row, identity in zip(c['observations'], expected):
    assert tuple(row[k] for k in ['kind', 'case', 'n', 'pair', 'side']) == identity
    kind, case, n, pair, side = identity
    assert row['exitCode'] == 0
    for stream in ['stdout', 'stderr']:
        name = f'{kind}-{case}-n{n}-pair{pair}-{side}.{stream}'
        assert row[stream] == name and sha(p / 'raw' / name) == row[stream + 'Sha256']
        files.add(name)
    assert (p / 'raw' / row['stderr']).read_bytes() == b''
    raw = (p / 'raw' / row['stdout']).read_text()
    assert raw.endswith('PASS\n')
    if kind == 'benchmark':
        lines = [line for line in raw.splitlines() if line.startswith('Benchmark')]
        assert len(lines) == 1
        match = re.fullmatch(rf'BenchmarkStorage/{case}/{side}/n{n}(?:-(\d+))?\s+(\d+)\s+([0-9.e+]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op', lines[0].strip())
        assert match
        cpu, it, ns, byt, alloc = match.groups()
        assert [int(cpu or 1), int(it), float(ns), int(byt), int(alloc)] == [row[k] for k in ['cpus', 'iterations', 'nsPerOp', 'bytesPerOp', 'allocsPerOp']]
        assert int(it) > 0 and float(ns) > 0
        assert row['command'] == [v['build']['binary'], '-test.run=^$', f'-test.bench=^BenchmarkStorage$/^{case}$/^{side}$/^n{n}$', '-test.benchtime=200ms', '-test.benchmem', '-test.count=1']
    else:
        lines = [line.split('RETENTION ', 1)[1] for line in raw.splitlines() if 'RETENTION ' in line]
        assert len(lines) == 1
        d = json.loads(lines[0]); assert d == row['retention']
        assert (d['side'], d['shape'], d['records'], d['rootPayload']) == (side, case, n, n * 0x100000001)
        for delta, key in [('heapAllocDelta', 'HeapAlloc'), ('heapObjectsDelta', 'HeapObjects'), ('totalAllocDelta', 'TotalAlloc')]:
            assert d[delta] == d['after'][key] - d['before'][key]
        assert d['after']['NumGC'] >= d['before']['NumGC'] + 2
        assert d['compactAllocatedSlots'] == (n if side == 'compact' else 0)
        assert row['command'] == [v['build']['binary'], '-test.run=^TestStorageRetentionProbe$', '-test.v', '-test.count=1']
assert files == {f.name for f in (p / 'raw').iterdir()}
summary = {'captureSha256': sha(p / 'capture.json'), 'verifiedObservations': 148, 'validationPasses': 21, 'benchmarks': [], 'retention': []}
median = statistics.median
for kind, cases in [('benchmark', cfg['operations']), ('retention', cfg['shapes'])]:
    for n in cfg['sizes']:
        for case in cases:
            rows = [r for r in c['observations'] if (r['kind'], r['case'], r['n']) == (kind, case, n)]
            sides = {s: sorted([r for r in rows if r['side'] == s], key=lambda r: r['pair']) for s in cfg['sides']}
            out = {'case': case, 'n': n}
            if kind == 'benchmark':
                a, b = ([r['nsPerOp'] for r in sides[s]] for s in cfg['sides'])
                ratios = [x / y for x, y in zip(a, b)]
                out.update(ratioOfMedians=median(a)/median(b), medianPairedRatio=median(ratios), pairedRange=[min(ratios), max(ratios)])
                for s in cfg['sides']:
                    out[s] = {k: median(r[k] for r in sides[s]) for k in ['nsPerOp', 'bytesPerOp', 'allocsPerOp']}
                summary['benchmarks'].append(out)
            else:
                for s in cfg['sides']:
                    out[s] = {k: median(r['retention'][k] for r in sides[s]) for k in ['heapAllocDelta', 'heapObjectsDelta', 'totalAllocDelta']}
                summary['retention'].append(out)
print(json.dumps(summary, indent=2))
