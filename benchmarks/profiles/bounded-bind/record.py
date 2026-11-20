"""Recompute screen medians from the paired samples and phase diagnostics."""
import json
from pathlib import Path
import re
import statistics
import sys

here = Path(__file__).resolve().parent
perf = here.parents[2] / 'PERF.md'
out = []
for arg in sys.argv[1:]:
    directory = here / arg
    data = json.loads((directory / 'report.json').read_text())
    for project, modes in data['medians'].items():
        samples = [r for r in data['samples'] if r['project'] == project]
        pairs = max(s['pair'] for s in samples)
        assert len(samples) == 2 * (pairs + 1)
        for i in range(pairs + 1):
            pair = [s for s in samples if s['pair'] == i]
            assert [s['bounded'] for s in pair] == ([1, 0] if i % 2 else [0, 1])
            for sample in pair:
                log = directory / f"{project}-{i}-{sample['bounded']}.log"
                phase = re.search(r'^Bind time:\s*([.\d]+)s$', log.read_text(), re.M)
                assert sample['bindMs'] == float(phase[1]) * 1000
        for mode in [0, 1]:
            rows = [r for r in samples if r['bounded'] == mode and r['pair']]
            for k in ['bindMs', 'wallMs', 'cpuSec', 'rssKiB']:
                assert statistics.median(r[k] for r in rows) == modes[str(mode)][k]
        a, b = modes['0'], modes['1']
        report_path = (directory / 'report.json').relative_to(here.parents[2])
        out.append(f"| Bounded binder worker screen | {project} | Same binary, one goroutine per unbound file | {a['wallMs']:.2f} | {b['wallMs']:.2f} | {a['wallMs']/b['wallMs']:.3f}× | {pairs} | Extended diagnostics, GNU time. Median bind {a['bindMs']:.1f}/{b['bindMs']:.1f} ms. [Samples]({report_path}) |")
assert out and all(row not in perf.read_text() for row in out)
with perf.open('a') as f:
    f.write('\n'.join(out) + '\n')
