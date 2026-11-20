"""Verify an official harness report, archive it, and append its table rows."""
import gzip
import hashlib
import json
from pathlib import Path
import statistics
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
source = Path(sys.argv[1])
raw = source.read_bytes()
data = json.loads(raw)
assert data['status'] == 'passed' and data['warmups'] == 1
for binary in data['binaries'].values():
    assert hashlib.sha256(Path(binary['path']).read_bytes()).hexdigest() == binary['sha256']
prior = json.loads((root / f'benchmarks/results/native-project-inlining/{source.name}').read_text())
assert data['binaries']['baseline']['sha256'] == prior['binaries']['candidate']['sha256']
archive = here / (source.name + '.gz')
assert not archive.exists()
rows = []
for p in data['projects']:
    expected = next(r for r in prior['projects'] if r['name'] == p['name'])
    assert p['status'] == 'passed' and p['commit'] == expected['commit']
    assert p['preflight']['candidate']['inputs'] == p['preflight']['baseline']['inputs'] == expected['preflight']['candidate']['inputs']
    assert p['args'] == expected['args'] and p['diagnosticCount'] == expected['diagnosticCount'] == 0
    medians = {}
    for mode in ('baseline', 'candidate'):
        samples = [q[mode] for q in p['pairs']]
        assert samples == p[mode]['samplesMs'] and len(samples) == data['runs']
        medians[mode] = statistics.median(samples)
        assert medians[mode] == p[mode]['medianMs']
    a, b = medians['baseline'], medians['candidate']
    assert abs(a/b - p['speedup']) < 1e-10
    rows.append(f"| Completed import task reuse | {p['name']} | Production Go | {a:.2f} | {b:.2f} | {a/b:.3f}× | {len(samples)} | Fresh processes, one warmup per binary. [Samples]({archive.relative_to(root)}) |")
perf = root / 'PERF.md'
assert rows and all(row not in perf.read_text() for row in rows)
archive.write_bytes(gzip.compress(raw, mtime=0))
assert gzip.decompress(archive.read_bytes()) == raw
with perf.open('a') as f:
    f.write('\n'.join(rows)+'\n')
