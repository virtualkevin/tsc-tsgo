"""Alternate fresh processes and capture compiler phases, wall time, CPU and RSS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument('binary', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('projects', nargs='+')
parser.add_argument('--pairs', type=int, default=4)
args = parser.parse_args()
assert args.pairs > 0
root = Path(__file__).resolve().parents[3]
binary = args.binary.resolve()
args.output.mkdir()
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root / 'upstream/typescript-go/internal/bundled/libs')
projects = {
    p['name']: p for group in ('small', 'large')
    for p in json.loads((root / f'benchmarks/results/native-project-inlining/{group}.json').read_text())['projects']
}
expected = json.loads((root / 'benchmarks/profiles/contiguous-checker-locality/results/report.json').read_text())
report = {'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'samples': [], 'medians': {}}
for project_name in args.projects:
    project = projects[project_name]
    cwd = Path(project['cwd'])
    counts = next(r['counts'] for r in expected['runs'] if r['project'] == project_name and r['scheduler'] == 'default')
    for item in project['preflight']['candidate']['inputs']:
        assert hashlib.sha256((cwd / item['file']).read_bytes()).hexdigest() == item['sha256']
    for pair in range(args.pairs + 1):
        for bounded in ((1, 0) if pair % 2 else (0, 1)):
            with tempfile.TemporaryDirectory() as temp:
                usage = Path(temp) / 'usage'
                cmd = ['/usr/bin/time', '-f', '%U %S %M', '-o', usage, binary, *project['args'],
                       '--checkers', '4', '--extendedDiagnostics']
                start = time.monotonic_ns()
                run = subprocess.run(cmd, cwd=cwd, env=env | {'TSC_GO_BOUNDED_BIND': str(bounded)},
                                     text=True, capture_output=True, check=True, timeout=400)
                wall_ms = (time.monotonic_ns() - start) / 1e6
                user, system, rss = usage.read_text().split()
            label = f'{project_name}-{pair}-{bounded}'
            (args.output / f'{label}.log').write_text(run.stdout)
            assert not run.stderr and not re.search(r'error TS\d+', run.stdout)
            for k in ['Files', 'Lines', 'Identifiers', 'Types', 'Instantiations']:
                assert re.search(rf'^{k}:\s*{counts[k]}\s*$', run.stdout, re.M), (label, k)
            bind = re.search(r'^Bind time:\s*([.\d]+)s$', run.stdout, re.M)
            assert bind
            report['samples'].append(dict(project=project_name, pair=pair, bounded=bounded, wallMs=wall_ms,
                                          cpuSec=float(user)+float(system), rssKiB=int(rss), bindMs=float(bind[1])*1000))
            (args.output / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
    summary = {}
    for mode in [0, 1]:
        rows = [r for r in report['samples'] if r['project'] == project_name and r['bounded'] == mode and r['pair']]
        summary[mode] = {k: statistics.median(r[k] for r in rows) for k in ['bindMs','wallMs','cpuSec','rssKiB']}
    report['medians'][project_name] = summary
    (args.output / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(project_name, summary, flush=True)
