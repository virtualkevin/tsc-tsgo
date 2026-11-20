"""Compare checker work counters for two file assignments in the same binary."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
binary = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2])
output.mkdir()
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root / 'upstream/typescript-go/internal/bundled/libs')
report = {'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'runs': []}
for group in ['small', 'large']:
    reference = root / f'benchmarks/results/native-project-inlining/{group}.json'
    for project in json.loads(reference.read_text())['projects']:
        cwd = Path(project['cwd'])
        for item in project['preflight']['candidate']['inputs']:
            assert hashlib.sha256((cwd / item['file']).read_bytes()).hexdigest() == item['sha256']
        for mode in ['default', 'contiguous']:
            args = [str(binary), *project['args'], '--checkers', '4', '--extendedDiagnostics']
            proc = subprocess.run(args, cwd=cwd, env=env | {'TSC_GO_SCHEDULER': mode}, capture_output=True, text=True, timeout=400)
            label = f"{project['name']}-{mode}"
            (output / (label + '.stdout')).write_text(proc.stdout)
            (output / (label + '.stderr')).write_text(proc.stderr)
            proc.check_returncode()
            assert not proc.stderr and not re.search(r'error TS\d+', proc.stdout)
            counts = {k: int(v) for k, v in re.findall(r'^(Files|Lines|Identifiers|Symbols|Types|Instantiations):\s*(\d+)\s*$', proc.stdout, re.M)}
            assert len(counts) == 6 and counts['Files'] == project['preflight']['candidate']['fileCount']
            report['runs'].append({'project': project['name'], 'scheduler': mode, 'command': args, 'counts': counts})
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(label, counts, flush=True)
