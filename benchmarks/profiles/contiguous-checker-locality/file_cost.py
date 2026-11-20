"""Capture file callback work on an isolated build with file-cost.patch applied."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
root = here.parents[2]
binary = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
output.mkdir()
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root / 'upstream/typescript-go/internal/bundled/libs')
projects = {
    p['name']: p
    for group in ('small', 'large')
    for p in json.loads((root / f'benchmarks/results/native-project-inlining/{group}.json').read_text())['projects']
}
report = {'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'runs': []}
reference_runs = json.loads((here / 'results/report.json').read_text())['runs']
for project_name in sys.argv[3:]:
    project = projects[project_name]
    cwd = Path(project['cwd'])
    for item in project['preflight']['candidate']['inputs']:
        assert hashlib.sha256((cwd / item['file']).read_bytes()).hexdigest() == item['sha256']
    for mode in ('default', 'contiguous'):
        reference = next(r for r in reference_runs if (r['project'], r['scheduler']) == (project_name, mode))
        with tempfile.TemporaryDirectory() as temp:
            log = Path(temp) / 'batch.jsonl'
            run = subprocess.run([binary, *reference['command'][1:]], cwd=cwd,
                                 env=env | {'TSC_GO_SCHEDULER': mode, 'TSC_GO_COST_LOG': str(log)},
                                 capture_output=True, text=True, timeout=400, check=True)
            assert not run.stderr and not re.search(r'error TS\d+', run.stdout)
            raw = log.read_bytes()
        counts = dict(re.findall(r'^(Files|Lines|Identifiers|Types|Instantiations):\s*(\d+)\s*$', run.stdout, re.M))
        assert len(counts) == 5 and all(int(v) == reference['counts'][k] for k, v in counts.items())
        rows = [row for line in raw.splitlines() for row in json.loads(line)]
        assert rows and all(row['File'] and row['ElapsedNS'] >= 0 for row in rows)
        workers = []
        for worker in range(4):
            assigned = [row for row in rows if row['Checker'] == worker]
            workers.append({'callbacks': len(assigned),
                            'callbackMs': sum(row['ElapsedNS'] for row in assigned) / 1e6,
                            'instantiations': sum(row['Instantiations'] for row in assigned)})
        label = f'{project_name}-{mode}'
        (output / f'{label}.jsonl.gz').write_bytes(gzip.compress(raw, mtime=0))
        report['runs'].append({'project': project_name, 'scheduler': mode, 'workers': workers,
                               'counts': {k: int(v) for k, v in counts.items()},
                               'logSha256': hashlib.sha256(raw).hexdigest()})
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(label, workers, flush=True)
