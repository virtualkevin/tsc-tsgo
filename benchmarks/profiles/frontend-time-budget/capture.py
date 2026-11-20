"""Compare current native wall time with the Go compiler's timed NewProgram phase."""
import hashlib
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
env = {k: v for k, v in os.environ.items() if not k.startswith(('TSC_', 'TS_GO_', 'SCRIPTC_', 'GODEBUG', 'GOGC', 'GOMEMLIMIT', 'GOMAXPROCS'))}
env['TSC_TS_LIB_DIR'] = str(root/'upstream/typescript-go/internal/bundled/libs')
output = here/'report.json'
assert not output.exists()
expected = json.loads((here.parent/'contiguous-checker-locality/results/report.json').read_text())
report = {'status': 'running', 'samples': [], 'summary': {}}
for group in ('small','large'):
    old = json.loads((root/f'benchmarks/results/native-project-inlining/{group}.json').read_text())
    binaries = old['binaries']
    for b in binaries.values():
        assert hashlib.sha256(Path(b['path']).read_bytes()).hexdigest() == b['sha256']
    report['binaries'] = {k:{f:b[f] for f in ('path','sha256')} for k,b in binaries.items()}
    for p in old['projects']:
        cwd = Path(p['cwd'])
        manifest = p['preflight']['candidate']['inputs']
        assert manifest == p['preflight']['baseline']['inputs']
        counts = next(r['counts'] for r in expected['runs'] if r['project']==p['name'] and r['scheduler']=='default')
        def verify():
            for item in manifest:
                assert hashlib.sha256((cwd/item['file']).read_bytes()).hexdigest() == item['sha256']
        verify()
        for mode,b in binaries.items():
            proc = subprocess.run([b['path'], *p['fileDiscoveryArgs'][mode]], cwd=cwd, env=env, text=True,
                                  capture_output=True, timeout=400, check=True)
            assert not proc.stderr
            assert sorted(os.path.relpath(cwd / path, cwd) for path in proc.stdout.splitlines()) == sorted(i['file'] for i in manifest)
        for pair in range(3):
            for mode in (('candidate','baseline') if pair%2 else ('baseline','candidate')):
                args = [binaries[mode]['path'], *p['compilerArgs'][mode]]
                if mode == 'candidate':
                    args.append('--extendedDiagnostics')
                start = time.monotonic_ns()
                proc = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, timeout=400, check=True)
                elapsed = (time.monotonic_ns()-start)/1e6
                assert not proc.stderr and not re.search(r'error TS\d+',proc.stdout)
                row = dict(project=p['name'], mode=mode, pair=pair, elapsedMs=elapsed)
                if mode == 'baseline':
                    assert not proc.stdout
                else:
                    for k in ('Files','Lines','Identifiers','Types','Instantiations'):
                        assert re.search(rf'^{k}:\s*{counts[k]}\s*$',proc.stdout,re.M)
                    parse = re.search(r'^Parse time:\s*([\d.]+)s$',proc.stdout,re.M)
                    row.update(parseMs=1000*float(parse[1]), stdout=proc.stdout)
                report['samples'].append(row)
                output.write_text(json.dumps(report,indent=2)+'\n')
        verify()
        measured = [r for r in report['samples'] if r['project']==p['name'] and r['pair']>0]
        native = statistics.median(r['elapsedMs'] for r in measured if r['mode']=='baseline')
        parse = statistics.median(r['parseMs'] for r in measured if r['mode']=='candidate')
        report['summary'][p['name']] = dict(nativeMs=native, targetMs=native/10, goProgramMs=parse,
                                             programToTargetRatio=parse/(native/10))
        print(p['name'],report['summary'][p['name']],flush=True)
report['status']='passed'
output.write_text(json.dumps(report,indent=2)+'\n')
