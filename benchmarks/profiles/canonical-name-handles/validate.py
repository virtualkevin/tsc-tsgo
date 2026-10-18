"""Run isolated Name prototype tests; production compiler remains unchanged."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
module = root / 'packages/tsc-go'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
replace = {str(module / 'internal/ast' / filename): str(out / filename) for filename in ['name.go', 'name_test.go']}
assert all(not Path(k).exists() for k in replace)
sources = {k: sha(Path(v)) for k, v in replace.items()}
(out / 'overlay.json').write_text(json.dumps({'Replace': replace}, indent=2) + '\n')
env = os.environ.copy()
for key in list(env):
    if key.startswith(('TSC_', 'TS_GO_', 'SCRIPTC_')) or key in ['GOFLAGS', 'GOEXPERIMENT', 'GODEBUG', 'GOGC', 'GOMEMLIMIT', 'GOMAXPROCS']:
        env.pop(key, None)
env['GOCACHE'] = '/home/dev/.cache/go-build'
report = {'scope': 'Isolated Name prototype tests via overlay; no production integration, full compiler conformance, or speed claim.', 'sources': sources, 'controllerSha256': sha(Path(__file__)), 'passed': False, 'runs': []}
for mode in ['normal', 'race']:
    command = ['/tmp/tsc-toolchains/go/bin/go', 'test', *(['-race'] if mode == 'race' else []), '-overlay', str(out / 'overlay.json'), './internal/ast', '-run', '^TestCanonicalName', '-count=1', '-timeout', '10m', '-json']
    with (out / (mode + '.jsonl')).open('w') as stdout, (out / (mode + '.stderr')).open('w') as stderr:
        run = subprocess.run(command, cwd=module, env=env, stdout=stdout, stderr=stderr)
    events = [json.loads(line) for line in (out / (mode + '.jsonl')).read_text().splitlines()]
    tests = [(e['Test'], e['Action']) for e in events if e.get('Test') and e['Action'] in ['pass', 'fail', 'skip']]
    passed = run.returncode == 0 and len(tests) == 3 and all(t[1] == 'pass' for t in tests) and any(e['Action'] == 'pass' and 'Test' not in e for e in events)
    report['runs'].append({'mode': mode, 'command': command, 'exitCode': run.returncode, 'tests': tests, 'passed': passed, 'stdoutSha256': sha(out / (mode + '.jsonl')), 'stderrSha256': sha(out / (mode + '.stderr'))})
    (out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    assert passed, mode
    print(mode, 'passed', flush=True)
assert sources == {k: sha(Path(v)) for k, v in replace.items()}
report['passed'] = True
(out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
