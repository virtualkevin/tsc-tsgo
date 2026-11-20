"""Count the import requests resolved by the shortcut during file discovery."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
binary = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2])
assert not output.exists()
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root / 'upstream/typescript-go/internal/bundled/libs')
report = {'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'runs': []}
for group in ['small','large']:
    reference = root / f'benchmarks/results/native-project-inlining/{group}.json'
    for project in json.loads(reference.read_text())['projects']:
        cwd = Path(project['cwd'])
        inputs = project['preflight']['candidate']['inputs']
        paths = sorted((cwd / f['file']).resolve() for f in inputs)
        for item in inputs:
            assert hashlib.sha256((cwd / item['file']).read_bytes()).hexdigest() == item['sha256']
        for mode in ('0','1'):
            proc = subprocess.run([binary, *project['fileDiscoveryArgs']['candidate']], cwd=cwd,
                                  env=env | {'TSC_GO_REUSE_LOADED_TASKS': mode}, text=True,
                                  capture_output=True, check=True, timeout=400)
            assert sorted((cwd / line).resolve() for line in proc.stdout.splitlines()) == paths
            batch = [re.fullmatch(r'parse edges (\d+) reused (\d+)', line) for line in proc.stderr.splitlines()]
            assert batch and all(batch), proc.stderr
            edges = sum(int(m[1]) for m in batch)
            reused = sum(int(m[2]) for m in batch)
            assert 0 <= reused <= edges and (mode == '1' or reused == 0)
            row = dict(project=project['name'], enabled=mode=='1', files=len(paths),
                       edges=edges, reused=reused, batches=proc.stderr.splitlines())
            report['runs'].append(row)
            output.write_text(json.dumps(report, indent=2)+'\n')
            print(row, flush=True)
