"""Capture interface member syntax by observed member retrieval and merge activity."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
binary = Path(sys.argv[1]).resolve()
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root / 'upstream/typescript-go/internal/bundled/libs')
expected = json.loads((here.parent / 'contiguous-checker-locality/results/report.json').read_text())
report = {'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'runs': []}
for group in ('small','large'):
    reference = root / f'benchmarks/results/native-project-inlining/{group}.json'
    for project in json.loads(reference.read_text())['projects']:
        cwd = Path(project['cwd'])
        preflight = project['preflight']['candidate']
        for item in preflight['inputs']:
            assert hashlib.sha256((cwd / item['file']).read_bytes()).hexdigest() == item['sha256']
        result = subprocess.run([binary, *project['args'], '--extendedDiagnostics'], cwd=cwd, env=env,
                                text=True, capture_output=True, check=True, timeout=400)
        counts = json.loads(result.stderr)
        assert counts['Files'] == preflight['fileCount']
        assert sum(counts['MemberNodes']) <= counts['SkippedDeclarationNodes'] <= counts['Nodes']
        assert sum(counts['Lists']) > 0 and counts['MemberNodes'][0] > 0
        assert not re.search(r'error TS\d+', result.stdout)
        ref = next(r for r in expected['runs'] if r['project'] == project['name'] and r['scheduler'] == 'default')
        for key in ['Files','Identifiers','Lines','Types','Instantiations']:
            assert re.search(rf'^{key}:\s*{ref["counts"][key]}\s*$', result.stdout, re.M), key
        report['runs'].append({'project': project['name'], 'counts': counts, 'stdout': result.stdout})
        (here / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(project['name'], counts, flush=True)
