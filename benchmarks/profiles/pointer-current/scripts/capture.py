#!/usr/bin/env python3
"""Prepared only. Launch after coordinator releases profiling; never benchmark these times."""
import datetime
import hashlib
import json
import os
import pathlib
import re
import signal
import subprocess
import sys
import time

ROOT = pathlib.Path('/home/dev/tssss/tsc-tsgo')
BINARY = ROOT / 'packages/tsc-go/dist/tsc-go-pointer-linkstore'
BINARY_SHA = 'b1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322'
SOURCE_SHA = '6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d'
SIDECAR = pathlib.Path(str(BINARY) + '.provenance.json')
BASIS = ROOT / 'benchmarks/results/pointer-linkstore-default-rss'
MANIFEST = ROOT / 'benchmarks/workloads.json'
LIBRARY = ROOT / 'upstream/typescript-go/internal/bundled/libs'
NAMES = ['typeorm', 'trpc', 'vscode', 'sentry']
CLOCK = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
OUT = pathlib.Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else pathlib.Path('/tmp') / ('tsc-pointer-profiles-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + str(os.getpid()))
OUT.mkdir()  # Reject any existing directory. Parent must already exist.
REPORT_PATH = OUT / 'capture.json'
report = {'schemaVersion': 1, 'status': 'running', 'startedAt': CLOCK(), 'purpose': 'Sequential CPU and allocation profile capture; no performance benchmark or speedup claim.', 'candidateRevisionLabel': '849d873', 'binary': str(BINARY), 'binarySha256': BINARY_SHA, 'sourceSha256': SOURCE_SHA, 'runs': [], 'methodology': 'Same semantic commands/inputs as completed pointer-default RSS reports; add explicit --checkers 4 and --pprofDir. Default GC and unset round-robin scheduler. Unwrapped profiled invocations are not comparable with wrapped benchmark times. No pprof analysis is executed automatically.', 'perInvocationTimeoutSeconds': 300, 'overallTimeoutSeconds': 1800, 'outputLimitBytesPerStream': 16 * 1024 * 1024}
active = None
cancelled = None
deadline = time.monotonic() + report['overallTimeoutSeconds']

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            require(cancelled is None and time.monotonic() < deadline, 'Cancelled or capture deadline exceeded while verifying inputs')
            h.update(block)
    return h.hexdigest()

def load(path):
    return json.loads(pathlib.Path(path).read_text())

def save():
    temp = OUT / 'capture.pending.json'
    temp.write_text(json.dumps(report, indent=2) + '\n')
    temp.replace(REPORT_PATH)

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def kill_group(child):
    if child is not None:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

def on_signal(number, frame):
    global cancelled
    cancelled = signal.Signals(number).name
    kill_group(active)

signal.signal(signal.SIGINT, on_signal)
signal.signal(signal.SIGTERM, on_signal)

def execute(command, cwd, prefix, env):
    global active
    require(cancelled is None, 'Interrupted: ' + str(cancelled))
    remaining = deadline - time.monotonic()
    require(remaining > 0, 'Overall capture deadline exceeded')
    limit = time.monotonic() + min(remaining, report['perInvocationTimeoutSeconds'])
    stdout, stderr = pathlib.Path(str(prefix) + '.stdout.log'), pathlib.Path(str(prefix) + '.stderr.log')
    child = None
    try:
        with stdout.open('xb') as out, stderr.open('xb') as err:
            child = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
            active = child
            while child.poll() is None:
                require(cancelled is None, 'Interrupted: ' + str(cancelled))
                require(time.monotonic() < limit, 'Capture command exceeded deadline')
                require(stdout.stat().st_size <= report['outputLimitBytesPerStream'] and stderr.stat().st_size <= report['outputLimitBytesPerStream'], 'Capture output limit exceeded')
                try:
                    child.wait(timeout=min(0.25, max(0.001, limit - time.monotonic())))
                except subprocess.TimeoutExpired:
                    pass
        require(cancelled is None, 'Interrupted: ' + str(cancelled))
        require(stdout.stat().st_size <= report['outputLimitBytesPerStream'] and stderr.stat().st_size <= report['outputLimitBytesPerStream'], 'Capture output limit exceeded')
        return {'command': command, 'cwd': str(cwd), 'pid': child.pid, 'exitCode': child.returncode, 'stdout': str(stdout), 'stderr': str(stderr), 'stdoutSha256': digest(stdout), 'stderrSha256': digest(stderr)}
    finally:
        # Includes the success path: no descendants may outlive an invocation.
        kill_group(child)
        if child is not None:
            child.wait(timeout=10)
        active = None

def text(run, stream):
    return pathlib.Path(run[stream]).read_text().replace('\r\n', '\n')

def signature(stdout, stderr):
    return hashlib.sha256(json.dumps([stdout, stderr], ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def lexical(path, cwd):
    return pathlib.Path(os.path.abspath(os.path.join(cwd, path)))

try:
    require(sys.platform == 'linux', 'This capture controller uses Linux process groups')
    summary = load(BASIS / 'summary.json')
    require(summary['status'] == 'passed', 'Completed pointer A/B evidence required')
    require(summary['expected']['candidate']['sha256'] == BINARY_SHA and summary['expected']['candidate']['source'] == SOURCE_SHA, 'Wrong basis candidate')
    metadata = load(SIDECAR)
    require(metadata['binary']['sha256'] == BINARY_SHA and metadata['source']['sha256'] == SOURCE_SHA, 'Wrong candidate provenance')
    require(digest(BINARY) == BINARY_SHA, 'Wrong preserved binary')
    basis_paths = [BASIS / 'summary.json', BASIS / 'small.json', BASIS / 'large.json']
    immutable = {str(p): digest(p) for p in [BINARY, SIDECAR, MANIFEST, pathlib.Path(__file__).absolute(), *basis_paths]}
    report['immutableFiles'] = immutable
    report['buildProvenance'] = metadata
    report['sidecarSha256'] = immutable[str(SIDECAR)]
    report['basisReports'] = [str(p) for p in basis_paths]
    report['captureHost'] = {'uname': list(os.uname()), 'python': sys.version, 'affinityCpus': sorted(os.sched_getaffinity(0)), 'cgroupMembership': pathlib.Path('/proc/self/cgroup').read_text()}
    manifest = load(MANIFEST)
    projects = {}
    basis_environment = {'TSC_TS_LIB_DIR': str(LIBRARY)}
    cleared = set(summary['unsetEnvironment'])
    for group in ['small', 'large']:
        rpath = BASIS / (group + '.json')
        basis_run = next(x for x in summary['runs'] if x['name'] == group)
        require(basis_run['status'] == 'passed' and digest(rpath) == basis_run['reportSha256'], 'Changed basis report')
        r = load(rpath)
        require(r['status'] == 'passed' and r['manifestSha256'] == immutable[str(MANIFEST)], 'Wrong manifest or failed report')
        require(r['candidateCheckers'] is None and r['environment']['candidateEnvironmentOverrides'] == {}, 'Unexpected basis override')
        require(r['environment']['compilerEnvironments'] == {'baseline': basis_environment, 'candidate': basis_environment}, 'Unexpected basis runtime controls')
        bp = r['binaries']['candidate']['buildProvenance']
        require(r['binaries']['candidate']['sha256'] == BINARY_SHA and bp['status'] == 'verified' and bp['sidecarSha256'] == immutable[str(SIDECAR)] and bp['metadata'] == metadata, 'Basis provenance mismatch')
        cleared.update(r['environment']['unsetEnvironment'])
        for p in r['projects']:
            require(p['name'] not in projects and p['status'] == 'passed' and p['expectedExit'] == 0 and p['diagnosticCount'] == 0, 'Invalid project evidence')
            require(p['compilerArgs']['baseline'] == p['compilerArgs']['candidate'], 'Asymmetric basis options')
            require(p['preflight']['baseline']['inputs'] == p['preflight']['candidate']['inputs'], 'Asymmetric basis inputs')
            require(p['preflight']['candidate']['status'] == 0 and p['preflight']['candidate']['outputSha256'] == signature('', ''), 'Basis diagnostics were not clean')
            projects[p['name']] = p
    require(set(projects) == set(NAMES), 'Exactly four pinned workloads required')
    cleared.update(['GOGC', 'GOMEMLIMIT', 'GOMAXPROCS', 'GODEBUG', 'GOEXPERIMENT', 'GOCOVERDIR', 'GOTRACEBACK', 'NODE_OPTIONS', 'TS_GO_DEBUG_STACK_LIMIT', 'LLVM_PROFILE_FILE', 'CPUPROFILE', 'HEAPPROFILE', 'HEAPCHECK', 'PPROF_PATH', 'MALLOC_CONF', 'MALLOC_ARENA_MAX', 'MALLOC_TRIM_THRESHOLD_', 'GLIBC_TUNABLES', 'LD_PRELOAD', '_TSC_BENCH_OWNER'])
    cleared.update(k for k in os.environ if k.startswith(('TSC_', 'TS_GO_', 'SCRIPTC_', 'MIMALLOC_', 'MI_')))
    cleared.discard('TSC_TS_LIB_DIR')
    env = os.environ.copy()
    for key in cleared:
        env.pop(key, None)
    env.update(basis_environment)
    report['unsetEnvironment'] = sorted(cleared)
    report['compilerEnvironment'] = basis_environment
    save()

    def verify_immutable():
        for path, sha in immutable.items():
            require(digest(path) == sha, 'Immutable file changed: ' + path)

    for name in NAMES:
        p = projects[name]
        item = next(x for x in manifest['projects'] if x['name'] == name)
        cwd = lexical(item['directory'], ROOT)
        require(str(cwd) == p['cwd'] and p['commit'] == item['commit'], 'Wrong project root/pin')
        args = ['-p', item['project'], *item.get('args', []), '--noEmit', '--incremental', 'false', '--composite', 'false', '--noCheck', 'false', '--pretty', 'false']
        require(args == p['compilerArgs']['candidate'], 'Basis arguments differ from pinned manifest')
        require(not any(a.lower().startswith(('--checkers', '--pprof', '--cpuprofile', '--generatetrace')) for a in args), 'Existing scheduling/profiling override')
        args += ['--checkers', '4']
        directory = OUT / name
        directory.mkdir()
        entry = {'name': name, 'status': 'running', 'cwd': str(cwd), 'commit': item['commit'], 'basisCompilerArgs': p['compilerArgs']['candidate'], 'profileCompilerArgs': args, 'configSha256': p['configSha256'], 'lockfileSha256': p['lockfileSha256'], 'inputs': p['preflight']['candidate']['inputs']}
        report['runs'].append(entry)
        save()

        def verify_inputs(phase):
            verify_immutable()
            require(digest(cwd / item['project']) == p['configSha256'], 'Configuration changed')
            require(digest(cwd / item['lockfile']) == p['lockfileSha256'], 'Lockfile changed')
            for input_file in entry['inputs']:
                require(digest(lexical(input_file['file'], cwd)) == input_file['sha256'], 'Input changed: ' + input_file['file'])
            revision = execute(['git', 'rev-parse', 'HEAD'], cwd, directory / (phase + '-revision'), env)
            status = execute(['git', 'status', '--porcelain', '--untracked-files=no'], cwd, directory / (phase + '-status'), env)
            require(revision['exitCode'] == 0 and text(revision, 'stderr') == '' and text(revision, 'stdout').strip() == item['commit'], 'Workload revision changed')
            require(status['exitCode'] == 0 and text(status, 'stdout') == '' and text(status, 'stderr') == '', 'Tracked workload files changed')
            return {'revision': revision, 'status': status}

        entry['before'] = verify_inputs('before')
        discovery = execute([str(BINARY), *args, '--listFilesOnly'], cwd, directory / 'discovery', env)
        entry['discovery'] = discovery
        require(discovery['exitCode'] == 0 and text(discovery, 'stderr') == '', 'File discovery failed')
        actual_files = sorted(os.path.relpath(lexical(line, cwd), cwd) for line in text(discovery, 'stdout').splitlines() if line)
        require(actual_files == sorted(i['file'] for i in entry['inputs']), 'Discovered input set differs from benchmark evidence')
        require(len(actual_files) == p['preflight']['candidate']['fileCount'], 'Input count differs')
        entry['profileCommand'] = [str(BINARY), *args, '--pprofDir', str(directory)]
        save()
        entry['profile'] = execute(entry['profileCommand'], cwd, directory / 'profile', env)
        result = entry['profile']
        save()
        require(result['exitCode'] == 0 and text(result, 'stderr') == '', 'Profiled check failed or wrote stderr')
        profiles = {}
        for line in text(result, 'stdout').splitlines():
            match = re.fullmatch(r'(CPU|Memory) profile: (.+)', line)
            require(match is not None, 'Unexpected compiler output/diagnostic: ' + line)
            kind, filename = match.groups()
            require(kind not in profiles, 'Duplicate profile announcement')
            suffix = 'cpuprofile' if kind == 'CPU' else 'memprofile'
            path = directory / (str(result['pid']) + '-' + suffix + '.pb.gz')
            require(filename == str(path) and path.is_file() and not path.is_symlink(), 'Unexpected profile output path')
            with path.open('rb') as f:
                require(f.read(2) == b'\x1f\x8b', 'Invalid profile gzip header')
            require(path.stat().st_size > 2, 'Empty profile')
            profiles[kind] = {'path': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size}
        require(set(profiles) == {'CPU', 'Memory'}, 'Missing CPU or allocation profile')
        require({str(p) for p in directory.glob('*.pb.gz')} == {v['path'] for v in profiles.values()}, 'Unannounced extra profiles')
        entry['profiles'] = profiles
        entry['diagnostics'] = {'expectedExitCode': 0, 'actualExitCode': result['exitCode'], 'nonProfileOutputSha256': signature('', ''), 'diagnosticCount': 0, 'onlyExpectedProfileAnnouncements': True}
        entry['after'] = verify_inputs('after')
        entry['status'] = 'passed'
        save()
        print('Captured validated profiles:', name, flush=True)
    verify_immutable()
    report['status'] = 'passed'
except BaseException as error:
    report['status'] = 'failed'
    report['error'] = type(error).__name__ + ': ' + str(error)
    if report['runs'] and report['runs'][-1]['status'] == 'running':
        report['runs'][-1]['status'] = 'failed'
    print(report['error'], file=sys.stderr, flush=True)
finally:
    kill_group(active)
    if active is not None:
        active.wait(timeout=10)
    report['completedAt'] = CLOCK()
    report['limitations'] = ['Capture timestamps are operational records, not performance measurements.', 'CPU and heap profiles are sampled; allocation space/objects require separate pprof sample-index selection and are not peak RSS.', 'Ordinary environment variables remain inherited; secret values are not recorded.', 'Profile gzip headers and hashes are checked; semantic decoding/summarization is intentionally deferred.', 'Cooperative signals/timeouts clean process groups; external SIGKILL of this controller bypasses Python cleanup.']
    save()
    print('Profile capture report:', REPORT_PATH, flush=True)
sys.exit(0 if report['status'] == 'passed' else 130 if cancelled == 'SIGINT' else 143 if cancelled == 'SIGTERM' else 1)
