"""Untimed fixed-four counters; native total instantiations are unavailable."""
import datetime
import hashlib
import json
import os
import pathlib
import re
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / 'benchmarks/results/lazy-default-large.json'
SINGLE = ROOT / 'benchmarks/profiles/lazy-large-single-checker-work/comparison.json'
CONTROLS = ['GOGC', 'GOMEMLIMIT', 'GOMAXPROCS', 'GODEBUG', 'TSC_GO_SCHEDULER',
            'TSC_GO_SHARED_GLOBALS', 'TSC_TS_CHECKERS', 'TSC_TS_REGION',
            'TSC_TS_RECYCLE', 'TSC_TS_SIDE_STATE', 'TSC_TS_CHECKERS_TRACE']
COUNTERS = ['Types', 'Instantiations', 'SymbolLinkEntries', 'NodeLinkEntries', 'Signatures', 'RelationEntries']


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def extended(stdout):
    return {m.group(1): int(m.group(2).replace(',', '')) for m in re.finditer(
        r'^([A-Za-z][A-Za-z /()-]*?):\s+([\d,]+)\s*$', stdout, re.M)}


def native(stderr, stdout_counters):
    if re.search(r'^checkers: (?:single |thread \d+ failed:)', stderr, re.M):
        raise ValueError('Unexpected single/main checker trace or worker failure')
    plans = re.findall(r'^checkers: ordered (\d+) files ', stderr, re.M)
    if len(plans) != 1 or len(re.findall(r'^checkers: finished at ', stderr, re.M)) != 1:
        raise ValueError('Missing or ambiguous parallel plan/completion')
    rows = []
    pattern = re.compile(
        r'^checkers: thread (\d+) checked (\d+) files in [\d.]+ms, done at [\d.]+ms '
        r'\[start \d+ ready \d+ end \d+ types (\d+) inst (\d+) user \d+ sys \d+ '
        r'rss \S+MB symlinks (\d+) nodelinks (\d+) sigs (\d+) rel (\d+)\]$')
    for line in stderr.splitlines():
        if not re.match(r'^checkers: thread \d+ checked ', line):
            continue
        match = pattern.fullmatch(line)
        if match is None:
            raise ValueError('Unrecognized worker counter format: ' + line)
        values = list(map(int, match.groups()))
        rows.append({'index': values[0], 'checkedFiles': values[1],
                     'counters': dict(zip(COUNTERS, values[2:]))})
    if not rows or sum(row['checkedFiles'] for row in rows) != int(plans[0]):
        raise ValueError('Worker completion coverage does not match planned files')
    indices = sorted(set(row['index'] for row in rows))
    if indices != list(range(len(indices))) or len(indices) > 4:
        raise ValueError('Unexpected worker indices')
    sums = {key: sum(row['counters'][key] for row in rows) for key in COUNTERS}
    return {'workerRecords': rows, 'actualWorkerIndices': indices,
            'workerGenerations': len(rows), 'plannedFiles': int(plans[0]),
            'workerOnlyCounters': sums, 'reportingMainTypes': stdout_counters['Types'],
            'totalCounters': {'Types': sums['Types'] + stdout_counters['Types'],
                              'Instantiations': None},
            'instantiationCoverage': 'Unavailable: main reporting checker is not traced in compileInParallel; worker-only sum is retained separately.'}


def main():
    source = json.loads(SOURCE.read_text())
    single = json.loads(SINGLE.read_text())
    env = os.environ.copy()
    for key in CONTROLS:
        env.pop(key, None)
    env.update(single['environmentOverrides'])
    report = {
        'schemaVersion': 1, 'status': 'running',
        'purpose': 'Untimed fixed-four versus saved single-checker creation counters; concurrent validation may run. No elapsed-time, speed, memory, or total-semantic-work claims.',
        'startedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sourceBenchmark': str(SOURCE.relative_to(ROOT)), 'sourceBenchmarkSha256': digest(SOURCE),
        'singleCheckerEvidence': str(SINGLE.relative_to(ROOT)), 'singleCheckerEvidenceSha256': digest(SINGLE),
        'binaries': single['binaries'], 'candidateSourceSha256': single['candidateSourceSha256'],
        'unsetEnvironment': CONTROLS, 'environmentOverrides': single['environmentOverrides'],
        'requestedCheckers': 4, 'collectorBudgetSeconds': 180,
        'nativeDefaultPolicy': 'auto (availableParallelism, memory/library adjustment); this experiment explicitly requests four, not native default.',
        'goDefaultPolicy': 'four (explicitly requested here)',
        'limitations': [
            'One parallel sample per workload/compiler; native work stealing, retirement and ambient scheduling can change per-worker counts.',
            'Types count allocations including initialization; Instantiations count worker calls after active mapper misses, not equal-cost operations or all semantic work.',
            'Native trace covers each worker generation; indices are not deduplicated. Reporting-main Types are added separately because native mainThreadChecks(shared=true) is false.',
            'Native reporting-main Instantiations are unreported in the parallel path, so native all-checker Instantiations and its 4/1 ratio remain unavailable.',
            'Higher aggregate counts indicate extra creation under this schedule, not measured duplicate identities or a realizable speedup.',
        ], 'projects': []}
    def save():
        (OUT / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    def verify(project):
        cwd = pathlib.Path(project['cwd'])
        if subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd, text=True).strip() != project['commit']:
            raise ValueError('Input revision changed')
        if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=cwd, text=True).strip():
            raise ValueError('Tracked input changes')
        for entry in project['preflight']['candidate']['inputs']:
            if digest(cwd / entry['file']) != entry['sha256']:
                raise ValueError('Input changed: ' + entry['file'])
        for binary in report['binaries'].values():
            if digest(binary['path']) != binary['sha256']:
                raise ValueError('Preserved binary changed')
    save()
    deadline = time.monotonic() + 180
    try:
        for name in ['sentry', 'vscode']:
            project = next(p for p in source['projects'] if p['name'] == name)
            previous = next(p for p in single['projects'] if p['name'] == name)
            verify(project)
            record = {key: previous[key] for key in ['name', 'commit', 'cwd', 'scope', 'configSha256', 'lockfileSha256', 'inputCount', 'inputFileListSha256']}
            record.update(status='running', runs={})
            report['projects'].append(record)
            save()
            for key, binary in report['binaries'].items():
                args = project['compilerArgs'][key] + ['--checkers', '4', '--extendedDiagnostics']
                print('START', name, key, flush=True)
                try:
                    run = subprocess.run([binary['path'], *args], cwd=project['cwd'], env=env,
                                         capture_output=True, text=True, timeout=max(0.1, deadline - time.monotonic()))
                except subprocess.TimeoutExpired as error:
                    for suffix, content in [('stdout', error.stdout), ('stderr', error.stderr)]:
                        (OUT / f'{name}-{key}.{suffix}.log').write_bytes(content if isinstance(content, bytes) else (content or '').encode())
                    record['runs'][key] = {'args': args, 'status': 'timed-out', 'completeCountersAvailable': False}
                    raise
                stdout, stderr = OUT / f'{name}-{key}.stdout.log', OUT / f'{name}-{key}.stderr.log'
                stdout.write_text(run.stdout)
                stderr.write_text(run.stderr)
                counts = extended(run.stdout)
                result = {'args': args, 'exitCode': run.returncode, 'stdout': stdout.name,
                          'stderr': stderr.name, 'stdoutSha256': digest(stdout), 'stderrSha256': digest(stderr),
                          'extendedCounters': counts}
                record['runs'][key] = result
                save()
                if run.returncode or re.search(r'error TS\d+:', run.stdout + run.stderr):
                    raise ValueError('Compilation failed: ' + name + '/' + key)
                for counter in ['Files', 'Lines', 'Identifiers']:
                    if counts[counter] != previous['runs'][key]['extendedCounters'][counter]:
                        raise ValueError('Input counter differs from single-checker evidence: ' + counter)
                if key == 'baseline':
                    result.update(native(run.stderr, counts))
                else:
                    result['totalCounters'] = {counter: counts[counter] for counter in ['Types', 'Instantiations']}
                result['versusSingleChecker'] = {
                    counter: None if value is None else {
                        'single': previous['runs'][key]['workCounters'][counter], 'fixedFour': value,
                        'extra': value - previous['runs'][key]['workCounters'][counter],
                        'fourOverOne': value / previous['runs'][key]['workCounters'][counter]}
                    for counter, value in result['totalCounters'].items()}
                save()
                print('DONE', name, key, result['totalCounters'], flush=True)
            verify(project)
            record['status'] = 'complete'
            save()
        report['status'] = 'complete'
    except BaseException as error:
        report['status'] = 'failed'
        report['error'] = str(error)
        raise
    finally:
        report['finishedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()


if __name__ == '__main__':
    main()
