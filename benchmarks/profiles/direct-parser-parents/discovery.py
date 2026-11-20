"""Time standalone file discovery on the candidate and production binaries."""
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
captures = Path(sys.argv[1]).resolve()
root = here.parents[2]
env = {k:v for k,v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_'))}
env['TSC_TS_LIB_DIR'] = str(root/'upstream/typescript-go/internal/bundled/libs')
report = {'samples': [], 'medians': {}}
output = here/'discovery.json'
assert not output.exists()
for group in ('small','large'):
    full = json.loads((captures/(group+'.json')).read_text())
    assert full['status'] == 'passed'
    for b in full['binaries'].values():
        assert hashlib.sha256(Path(b['path']).read_bytes()).hexdigest()==b['sha256']
    for p in full['projects']:
        cwd = Path(p['cwd'])
        inputs = p['preflight']['candidate']['inputs']
        paths = sorted(i['file'] for i in inputs)
        for i in inputs:
            assert hashlib.sha256((cwd/i['file']).read_bytes()).hexdigest()==i['sha256']
        for pair in range(5):
            for mode in (('candidate','baseline') if pair%2 else ('baseline','candidate')):
                cmd = [full['binaries'][mode]['path'], *p['fileDiscoveryArgs'][mode]]
                start = time.monotonic_ns()
                proc = subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,check=True,timeout=400)
                elapsed = (time.monotonic_ns()-start)/1e6
                assert not proc.stderr and sorted(os.path.relpath(cwd/name,cwd) for name in proc.stdout.splitlines())==paths
                report['samples'].append(dict(project=p['name'],pair=pair,mode=mode,ms=elapsed))
                output.write_text(json.dumps(report,indent=2)+'\n')
        report['medians'][p['name']] = {k:statistics.median(s['ms'] for s in report['samples'] if s['project']==p['name'] and s['pair'] and s['mode']==k) for k in ('baseline','candidate')}
        print(p['name'],report['medians'][p['name']],flush=True)
output.write_text(json.dumps(report,indent=2)+'\n')
