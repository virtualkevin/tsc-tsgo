"""Verify captured observer evidence without rerunning the compiler."""
import hashlib
import json
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
report = read(out / 'report.json')
validation = read(out / 'validation.json')
build = read(out / 'build.json')
assert report['status'] == 'passed' and len(report['runs']) == 12
assert report['controllerSha256'] == sha(out / 'capture.py')
assert report['validationSha256'] == sha(out / 'validation.json')
assert validation['passed'] and len(validation['runs']) == 2
assert validation['controllerSha256'] == sha(out / 'validate.py')
assert build['exitCode'] == 0 and build['binarySha256'] == report['candidateSha256']
assert build['buildInfoSha256'] == sha(out / 'build-info.txt')
assert build['overlaySources'] == validation['overlaySources']
assert {str(Path(k).relative_to(root)): v for k, v in build['overlaySources'].items()} == report['overlaySources']
for run in validation['runs']:
    assert run['passed'] and run['exitCode'] == 0
    assert len(run['tests']) == 4 and all(t[1] == 'pass' for t in run['tests'])
    for suffix in ['stdout', 'stderr']:
        filename = run['mode'] + ('.jsonl' if suffix == 'stdout' else '.stderr')
        assert run[suffix + 'Sha256'] == sha(out / filename)
    events = [json.loads(s) for s in (out / (run['mode'] + '.jsonl')).read_text().splitlines()]
    assert not any(e['Action'] in ['fail', 'skip'] for e in events)
    assert sorted((e['Test'], e['Action']) for e in events if e.get('Test') and e['Action'] == 'pass') == sorted(map(tuple, run['tests']))
    assert any(e['Action'] == 'pass' and 'Test' not in e for e in events)
expected = {(project, mode) for project in ['typeorm', 'trpc', 'vscode', 'sentry'] for mode in ['baseline', 'disabled', 'enabled']}
assert {(r['project'], r['mode']) for r in report['runs']} == expected
summary = []
for run in report['runs']:
    work = out / run['project']
    assert run['exitStatus'] == 0
    for stream in ['stdout', 'stderr']:
        p = work / (run['mode'] + '.' + stream)
        assert sha(p) == run[stream + 'Sha256'] and p.read_bytes() == b''
    group = 'small' if run['project'] in ['typeorm', 'trpc'] else 'large'
    reference = root / f'benchmarks/results/native-node-pointer/{group}.json'
    assert sha(reference) == run['referenceSha256']
    project = next(p for p in read(reference)['projects'] if p['name'] == run['project'])
    assert run['cwd'] == project['cwd'] and run['command'][1:] == project['args']
    assert run['inputCount'] == len(project['preflight']['candidate']['inputs'])
    if run['mode'] != 'enabled':
        assert run['counts'] is None and run['censusSha256'] is None
        continue
    assert sha(work / 'census.json') == run['censusSha256']
    census = read(work / 'census.json')
    assert census['Labels'] == ['identifier-constructor', 'binder-symbol-constructor', 'checker-symbol-constructor']
    counts = census['Counts']
    assert counts == run['counts']
    masks = counts['MembershipMasks']
    assert len(masks) == 8 and masks[0] == 0 and sum(masks) == counts['Distinct']
    assert counts['LimitKeys'] == 1048576 and counts['LimitBytes'] == 67108864
    assert counts['Distinct'] <= counts['LimitKeys'] and counts['DistinctBytes'] <= counts['LimitBytes']
    assert len(counts['Categories']) == 3
    for i, c in enumerate(counts['Categories']):
        assert c['Untracked'] == 0  # These captures fit both caps.
        assert c['Distinct'] == sum(v for mask, v in enumerate(masks) if mask & (1 << i))
        assert c['Distinct'] <= c['Requests']
        assert c['DistinctBytes'] <= min(counts['DistinctBytes'], c['NameBytes'])
        assert len(c['LengthBuckets']) == 65 and sum(c['LengthBuckets']) == c['Requests']
        assert c['Empty'] == c['LengthBuckets'][0]
    summary.append({'project': run['project'], 'events': [c['Requests'] for c in counts['Categories']], 'distinctNames': counts['Distinct'], 'distinctBytes': counts['DistinctBytes']})
result = {'passed': True, 'scope': 'Archived capture integrity and accounting; not timing, full conformance, or a fresh physical-input check.', 'runs': 12, 'summary': summary}
(out / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
