"""Time round-robin and contiguous ownership using identical compiler builds and inputs."""
from pathlib import Path
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
probe = json.loads((here / 'results/report.json').read_text())
assert len(probe['runs']) == 8
binary = Path(sys.argv[1]).resolve()
assert hashlib.sha256(binary.read_bytes()).hexdigest() == probe['binarySha256']
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root / 'upstream/typescript-go/internal/bundled/libs')
output = here / 'timing.json'
assert not output.exists()
report = {'status': 'running', 'binarySha256': probe['binarySha256'], 'samples': [], 'mediansMs': {}}
for group in ['small', 'large']:
    reference = root / f'benchmarks/results/native-project-inlining/{group}.json'
    for project in json.loads(reference.read_text())['projects']:
        cwd = Path(project['cwd'])
        for item in project['preflight']['candidate']['inputs']:
            assert hashlib.sha256((cwd / item['file']).read_bytes()).hexdigest() == item['sha256']
        for pair in range(5):
            modes = ['default', 'contiguous'] if pair % 2 == 0 else ['contiguous', 'default']
            for mode in modes:
                start = time.monotonic_ns()
                run = subprocess.run([str(binary), *project['args'], '--checkers', '4'], cwd=cwd, env=env | {'TSC_GO_SCHEDULER': mode}, capture_output=True, timeout=300)
                elapsed = (time.monotonic_ns() - start) / 1e6
                run.check_returncode()
                assert not run.stdout and not run.stderr
                report['samples'].append(dict(project=project['name'], pair=pair, warmup=pair==0, mode=mode, ms=elapsed))
                output.write_text(json.dumps(report, indent=2) + '\n')
        medians = {m: statistics.median(s['ms'] for s in report['samples'] if s['project']==project['name'] and s['mode']==m and not s['warmup']) for m in modes}
        report['mediansMs'][project['name']] = medians
        print(project['name'], medians, flush=True)
report['status'] = 'passed'
output.write_text(json.dumps(report, indent=2) + '\n')
