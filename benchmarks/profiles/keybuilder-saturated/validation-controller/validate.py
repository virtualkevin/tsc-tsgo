#!/usr/bin/env python3
"""Preparation-only controller: run only after parent releases validation.
Never applies patches, builds release binaries, publishes, or changes source.
"""
import argparse
import collections
import hashlib
import json
import os
import pathlib
import re
import signal
import subprocess
import sys
import time

FOCUS = '^(TestBuffered|TestRelationKeys)'
FOCUSED_TESTS = {
    'TestBufferedKeyBuilderSaturatedStreamingLength',
    'TestBufferedDirectIntegerBoundaryTransitions',
    'TestBufferedKeyBuilderStreamingBoundaries',
    'TestBufferedKeyBuilderIntegerEncoding',
    'TestBufferedKeyBuilderPreservesLazyIdAssignmentOrder',
    'TestBufferedKeyBuilderAliasAndTypeEncoding',
    'TestBufferedKeyBuilderNestedBuildersAreIndependent',
    'TestBufferedTemplateKeyRetainsTextBoundaries',
    'TestRelationKeysRecursiveGenericAssignmentsAndDiagnostics',
    'TestRelationKeysColdRecursiveConstraints',
    'TestRelationKeysRepeatedFailureDiagnosticsKeepUsePositions',
}
EXPECTED_FILES = {
    'checker.go': '761427dae0126839bb6803be7fd88bed3dc4924d31b20edee1d72ca0d68981ee',
    'keybuilder.go': '6c50894e0b6c481c2878af208c31f575e15829025a594261cda3e9e10a16d13a',
    'keybuilder_direct_test.go': 'e397e66d6cb2da4566e517ec75fdd00c2dcbe02eceea0915bba1ad1631dee3db',
    'keybuilder_test.go': 'dba4b569b9e5528d1f8e59c91f1ff1ee369abcb406700c3a3af9f7013a82648a',
    'relater.go': '5e4638c881b4371c828a4a71cd1b2204a90c0aa4b1da8c9a5c1759f0b4c58aae',
    'relation_keys_api_test.go': 'e32a99d280fc626e4812705d21fe3f856ca9a7688777b91368d1c96a1dbae5ec',
}
EXPECTED_PINS = {
    'typescript_go': '2bd066d87f5bafd315be9f40889d0a60b9e58e0b',
    'typescript': '4d4f005c8541e0255a9d8791205fdce326e462bc',
}
ROOT_PACKAGES = {'core','ast','bundled','scanner','compiler','checker','tsgo','execute','build','watchmanager'}


def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def summarize_run(run):
    records = []; reasons = collections.defaultdict(list); statuses = {}; cached = set()
    with open(run['stdout']) as stream:
        for line in stream:
            if not line.startswith('{'): continue  # npm script headers
            event = json.loads(line)
            test = event.get('Test')
            if event['Action'] in ('pass','skip','fail'):
                if test: records.append(event)
                else: statuses[event['Package']] = event['Action']
            elif event['Action'] == 'output':
                text = event.get('Output','')
                if re.search(r'\.go:\d+: ', text): reasons[test].append(text)
                if '(cached)' in text: cached.add(event['Package'])
    counts = collections.Counter(e['Action'] for e in records)
    tops = [e for e in records if '/' not in e['Test']]
    top_passes = [e['Test'] for e in tops if e['Action']=='pass']
    errors = []
    if run['exit_code'] != 0: errors.append('nonzero process exit')
    if not statuses or any(v != 'pass' for v in statuses.values()): errors.append('missing or nonpassing package terminal status')
    if counts['fail']: errors.append('failed test events')
    value = {'test_records':dict(counts), 'top_level_records':dict(collections.Counter(e['Action'] for e in tops)), 'passing_top_level_tests':top_passes, 'package_status':statuses, 'cached_packages':sorted(cached)}
    if run['name'] in ('focused','race','checkptr'):
        if set(top_passes)!=FOCUSED_TESTS or len(tops)!=len(FOCUSED_TESTS): errors.append('focused test names/count differ from eleven expected top-level tests')
        if len(statuses)!=1 or not next(iter(statuses),'').endswith('/internal/checker'): errors.append('expected exactly the checker package')
        if counts['skip']: errors.append('focused test skipped')
        if counts['pass']!=655: errors.append('expected 655 passing records: eleven top-level + 240 mixed boundaries + 390 direct-writer boundaries + eight saturated-streaming + four encoding + two cold-order subtests')
        if cached: errors.append('focused run unexpectedly cached')
    elif run['name']=='root-npm':
        if len(statuses)!=10 or {p.rsplit('/',1)[-1] for p in statuses}!=ROOT_PACKAGES: errors.append('root alias package scope differs from expected ten packages')
        if cached: errors.append('root run unexpectedly cached')
        value['scope']='Current root npm test alias, forced uncached with GOFLAGS=-json -count=1.'
    elif run['name']=='conformance':
        parents = [e for e in records if e['Test'].startswith('TestSubmodule/') and e['Test'].count('/')==1]
        partial = [e for e in records if e['Action']=='skip' and e['Test'].startswith('TestSubmodule/') and e['Test'].count('/')>1]
        partial_parents = {'/'.join(e['Test'].split('/')[:2]) for e in partial}
        passed = {e['Test'] for e in parents if e['Action']=='pass'}
        pc = collections.Counter(e['Action'] for e in parents)
        def reason(event):
            lines = reasons[event['Test']]
            for line in lines:
                match = re.search(r'\.go:\d+: (.*)',line)
                if match: return match.group(1).strip()
            return ''.join(lines).strip()
        categories = collections.Counter()
        for event in parents:
            if event['Action']!='skip': continue
            text = reason(event)
            for prefix in ('unsupported baseUrl','unsupported outFile'):
                if text.startswith(prefix): text=prefix; break
            categories[text]+=1
        value.update(source_configuration_cases={'total':len(parents),'fully_checked':len(passed-partial_parents),'partially_checked':len(passed&partial_parents),'unsupported_skipped':pc['skip'],'failed':pc['fail']}, skip_categories=dict(categories), partial_output_skips=[{'test':e['Test'],'reason':reason(e)} for e in partial], failed_tests=[e['Test'] for e in records if e['Action']=='fail'])
        if top_passes!=['TestSubmodule'] or not parents or not passed: errors.append('missing completed full TestSubmodule execution')
        if len(statuses)!=1 or not next(iter(statuses),'').endswith('/internal/testrunner'): errors.append('unexpected conformance package')
        if cached: errors.append('conformance unexpectedly cached')
    value['integrity_errors']=errors
    return value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo',default='/home/dev/tssss/tsc-tsgo')
    ap.add_argument('--output',required=True,help='Fresh directory strictly below /tmp')
    ap.add_argument('--go',default='/tmp/tsc-toolchains/go/bin/go')
    ap.add_argument('--expected-source',required=True,help='Parent-approved complete captureGoSources SHA256 after applying reviewed patch')
    args = ap.parse_args()
    if not re.fullmatch('[0-9a-f]{64}',args.expected_source): ap.error('expected-source must be a complete SHA256')
    root=pathlib.Path(args.repo).resolve(); output=pathlib.Path(args.output).resolve(); pkg=root/'packages/tsc-go'
    if output==pathlib.Path('/tmp') or not output.is_relative_to('/tmp') or output.is_relative_to(root): ap.error('output must be a fresh directory below /tmp and outside source')
    output.mkdir(parents=True,exist_ok=False)
    env = os.environ.copy()
    cleared = sorted(k for k in env if k.startswith(('TSC_GO_','TSC_TS_')) or k in {'GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','GOOS','GOARCH','GOAMD64','GOTRACEBACK','GORACE','GOCOVERDIR'})
    for key in cleared: env.pop(key,None)
    env.update(PATH=str(pathlib.Path(args.go).parent)+':'+env.get('PATH',''),GOFLAGS='',CGO_ENABLED='1',GOTOOLCHAIN='local')
    results=[]; suites={}; snapshots={}; failure=None; child=None; interrupted=None
    def handle_signal(number, frame):
        nonlocal interrupted
        interrupted=number
        raise KeyboardInterrupt('signal '+str(number))
    for signum in (signal.SIGINT,signal.SIGTERM): signal.signal(signum,handle_signal)
    def small(command,cwd=root):
        return subprocess.check_output(command,cwd=cwd,env=env,text=True,timeout=60).strip()
    def capture(label):
        js='import {captureGoSources} from "./scripts/build-provenance.mjs"; console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
        value=json.loads(small(['node','--input-type=module','-e',js]))
        write(output/(label+'.json'),value)
        snapshots[label]={k:value[k] for k in ('revision','dirty','sha256','digestAlgorithm')}
        snapshots[label]['file_count']=len(value['files'])
        return value
    def pins():
        return {'typescript_go':small(['git','rev-parse','HEAD'],root/'upstream/typescript-go'),'typescript':small(['git','rev-parse','HEAD'],root/'upstream/TypeScript')}
    def kill_group(process):
        # A process-group kill also reaches compiler/test subprocesses, including
        # descendants remaining after their immediate leader exits.
        for signum in (signal.SIGTERM,signal.SIGKILL):
            try: os.killpg(process.pid,signum)
            except ProcessLookupError: pass
            if signum==signal.SIGTERM: time.sleep(0.5)
        process.wait(timeout=10)
    def run(name,command,cwd=pkg,overrides=None,timeout=2400):
        nonlocal child
        run_env=env|dict(overrides or {}); outpath=output/(name+'.jsonl'); errpath=output/(name+'.stderr')
        run_error=None; code=None; started=time.monotonic()
        try:
            with outpath.open('w') as out, errpath.open('w') as err:
                child=subprocess.Popen(command,cwd=cwd,env=run_env,stdout=out,stderr=err,start_new_session=True)
                try: code=child.wait(timeout=timeout)
                except (subprocess.TimeoutExpired,KeyboardInterrupt) as exc:
                    run_error=type(exc).__name__+': '+str(exc)
                    kill_group(child); code=child.returncode
                    if isinstance(exc,KeyboardInterrupt): raise
        finally:
            if child is not None:
                kill_group(child); code=child.returncode; child=None
            result={'name':name,'command':command,'cwd':str(cwd),'environment':{k:run_env.get(k) for k in ('GOFLAGS','CGO_ENABLED','GOTOOLCHAIN','GOARCH','GOOS','GOGC','GOMEMLIMIT','GOMAXPROCS')},'exit_code':code,'timeout_seconds':timeout,'duration_seconds_not_benchmark':time.monotonic()-started,'error':run_error,'stdout':str(outpath),'stderr':str(errpath),'stdout_sha256':digest(outpath),'stderr_sha256':digest(errpath)}
            results.append(result); write(output/'process-results.json',results)
            (output/(name+'.exit')).write_text(str(code)+'\n')
            print(name,code,flush=True)
        suites[name]=summarize_run(result)
        after=capture('source-after-'+name)
        if after['sha256']!=args.expected_source or after['revision']!=snapshots['source-before']['revision']: raise RuntimeError('source or HEAD changed during '+name)
        if run_error or suites[name]['integrity_errors']: raise RuntimeError(name+': '+str(run_error or suites[name]['integrity_errors']))
    toolchain=None; fixture_before=None; fixture_after=None
    try:
        before=capture('source-before')
        if before['sha256']!=args.expected_source: raise RuntimeError('source digest differs from parent-approved source; no tests started')
        for name,expected in EXPECTED_FILES.items():
            if digest(pkg/'internal/checker'/name)!=expected: raise RuntimeError('reviewed patch/retained source mismatch: '+name)
        checker=(pkg/'internal/checker/checker.go').read_text()
        if 'type RelationKey uint64' in checker or (pkg/'internal/checker/relation_keys_test.go').exists(): raise RuntimeError('numeric relations rollback incomplete')
        fixture_before=pins()
        if fixture_before!=EXPECTED_PINS: raise RuntimeError('fixture revisions differ from pinned versions')
        toolchain=small([args.go,'version'])
        if not re.search(r'\bgo1\.26\.9\b',toolchain): raise RuntimeError('expected pinned Go 1.26.9')
        run('focused',[args.go,'test','-json','./internal/checker','-run',FOCUS,'-count=1','-timeout','20m'])
        run('race',[args.go,'test','-json','-race','./internal/checker','-run',FOCUS,'-count=1','-timeout','20m'])
        run('checkptr',[args.go,'test','-json','-gcflags=all=-d=checkptr=2','./internal/checker','-run',FOCUS,'-count=1','-timeout','20m'])
        run('root-npm',['npm','test'],root,{'GOFLAGS':'-json -count=1'},timeout=3600)
        run('conformance',[args.go,'test','-json','./internal/testrunner','-run','^TestSubmodule$','-parallel','4','-count=1','-timeout','30m'],timeout=2400)
    except (Exception,KeyboardInterrupt) as exc:
        failure=type(exc).__name__+': '+str(exc)
        print(failure,file=sys.stderr,flush=True)
    finally:
        if child is not None: kill_group(child)
        try: capture('source-after'); fixture_after=pins()
        except Exception as exc: failure=(failure or '')+'; final capture failed: '+str(exc)
        unchanged=bool(snapshots) and all(v['sha256']==args.expected_source and v['revision']==snapshots.get('source-before',{}).get('revision') for v in snapshots.values()) and 'source-after' in snapshots
        complete=len(results)==5 and all(r['exit_code']==0 and not r['error'] for r in results) and len(suites)==5 and all(not s['integrity_errors'] for s in suites.values())
        report={'schema_version':1,'candidate':'saturated streaming length for direct buffered keyBuilder writers; original 128-bit relation keys','controller_sha256':digest(pathlib.Path(__file__)),'expected_source_sha256':args.expected_source,'reviewed_files_sha256':EXPECTED_FILES,'toolchain':toolchain,'fixture_revisions_before':fixture_before,'fixture_revisions_after':fixture_after,'fixtures_unchanged':fixture_before==fixture_after==EXPECTED_PINS,'source_snapshots':snapshots,'source_unchanged':unchanged,'cleared_environment_variable_names':cleared,'processes':results,'suites':suites,'validation_incomplete':not complete,'failure':failure,'signal':interrupted,'coverage_limits':['Go test compiles normal/race/checkptr test binaries; this controller does not build or validate the separately produced release/native binary.','Focused regexp requires exactly eleven named top-level tests; actual nested subtest counts are recorded, with no focused skips permitted.','Race instrumentation covers executed code paths; no claim of deliberate simultaneous checker mutation.','Root npm test executes ten packages uncached, followed sequentially by the full pinned TestSubmodule suite.','Unsupported and partially checked conformance cases are counted separately; they are not full semantic passes.','Pinned revision identity is checked before/after; TypeScript corpus content is not independently hashed by this controller.','Native CLI/API/parallel emit validation is separate; durations here are not performance measurements.']}
        report['passed']=complete and unchanged and report['fixtures_unchanged'] and failure is None
        write(output/'validation.json',report)
        print('terminal passed='+str(report['passed'])+' source_unchanged='+str(unchanged),flush=True)
    return 0 if report['passed'] else 1


if __name__=='__main__': sys.exit(main())
