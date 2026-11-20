"""Record completed paired timings after verifying identical workloads and counts."""
import json
import re
import statistics
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[2]
timing = json.loads((here / 'timing.json').read_text())
probe = json.loads((here / 'results/report.json').read_text())
assert timing['status'] == 'passed' and probe['binarySha256'] == timing['binarySha256']
assert len(probe['runs']) == 8 and len(timing['samples']) == 40
rows = []
for project in ['typeorm', 'trpc', 'vscode', 'sentry']:
    counts = {}
    for mode in ['default', 'contiguous']:
        [run] = [r for r in probe['runs'] if r['project'] == project and r['scheduler'] == mode]
        prefix = here / 'results' / f'{project}-{mode}'
        assert prefix.with_suffix('.stderr').read_bytes() == b''
        for key, count in run['counts'].items():
            assert re.search(rf'^{key}:\s*{count}\s*$', prefix.with_suffix('.stdout').read_text(), re.M)
        counts[mode] = run['counts']
    for key in ['Files', 'Lines', 'Identifiers']:
        assert counts['default'][key] == counts['contiguous'][key]
    samples = [s for s in timing['samples'] if s['project'] == project]
    for i in range(5):
        pair = [s for s in samples if s['pair'] == i]
        assert [s['mode'] for s in pair] == (['contiguous','default'] if i % 2 else ['default','contiguous'])
        assert all(s['warmup'] == (i == 0) and s['ms'] > 0 for s in pair)
    medians = {m: statistics.median(s['ms'] for s in samples if not s['warmup'] and s['mode'] == m) for m in counts}
    assert medians == timing['mediansMs'][project]
    base, candidate = medians['default'], medians['contiguous']
    rows.append(f"| Contiguous file ownership | {project} | Same binary, round-robin, four checkers | {base:.2f} | {candidate:.2f} | {base/candidate:.3f}× | 4 | Fresh processes, one warmup per mode. [Samples](benchmarks/profiles/contiguous-checker-locality/timing.json) |")
    print(project, medians, round(base / candidate, 3))
perf = root / 'PERF.md'
assert all(row not in perf.read_text() for row in rows)
with perf.open('a') as out:
    out.write('\n'.join(rows) + '\n')
