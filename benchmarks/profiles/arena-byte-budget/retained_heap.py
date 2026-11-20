"""Compare the compiler's post-GC heap and total allocation count on pinned projects."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
captures = Path(sys.argv[1]).resolve()
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root/'upstream/typescript-go/internal/bundled/libs')
report = []
for group in ('small','large'):
    screen = json.loads((captures/(group+'.json')).read_text())
    assert screen['status'] == 'passed'
    for project in screen['projects']:
        cwd = Path(project['cwd'])
        for item in project['preflight']['candidate']['inputs']:
            assert hashlib.sha256((cwd/item['file']).read_bytes()).hexdigest() == item['sha256']
        by_mode = {}
        for mode in ('baseline','candidate'):
            b = screen['binaries'][mode]
            assert hashlib.sha256(Path(b['path']).read_bytes()).hexdigest() == b['sha256']
            proc = subprocess.run([b['path'], *project['args'], '--extendedDiagnostics'], cwd=cwd, env=env,
                                  capture_output=True, text=True, check=True, timeout=400)
            assert not proc.stderr and not re.search(r'error TS\d+',proc.stdout)
            by_mode[mode] = {k:int(v) for k,v in re.findall(r'^(Files|Lines|Identifiers|Types|Instantiations|Memory used|Memory allocs):\s*(\d+)K?\s*$',proc.stdout,re.M)}
            assert len(by_mode[mode]) == 7
        for k in ('Files','Lines','Identifiers','Types','Instantiations'):
            assert by_mode['baseline'][k] == by_mode['candidate'][k]
        report.append({'project':project['name'], 'counts':by_mode})
        (here/'retained-heap.json').write_text(json.dumps(report,indent=2)+'\n')
        print(project['name'],by_mode,flush=True)
