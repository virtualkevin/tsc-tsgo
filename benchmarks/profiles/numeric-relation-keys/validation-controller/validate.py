#!/usr/bin/env python3
"""Prepared controller only. Does not apply patches, build release binaries or commit.
Run after the parent selects/applies the baseline and explicitly releases timing.
"""
import argparse, collections, concurrent.futures, hashlib, json, os, pathlib, re, subprocess, sys, threading

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='/home/dev/tssss/tsc-tsgo')
    ap.add_argument('--output', required=True, help='Fresh directory under /tmp; existing output is rejected')
    ap.add_argument('--go', default='/tmp/tsc-toolchains/go/bin/go')
    ap.add_argument('--expected-source', required=True, help='Parent-approved complete captureGoSources SHA256 after patch integration')
    args = ap.parse_args()
    root = pathlib.Path(args.repo).resolve(); output = pathlib.Path(args.output).resolve()
    if not output.is_relative_to(pathlib.Path('/tmp')):
        ap.error('Draft controller writes artifacts only below /tmp')
    output.mkdir(parents=True, exist_ok=False)
    pkg = root/'packages/tsc-go'
    checker = (pkg/'internal/checker/checker.go').read_text()
    relater = (pkg/'internal/checker/relater.go').read_text()
    if 'type RelationKey uint64' not in checker or 'map[RelationKey]RelationComparisonResult' not in relater:
        raise SystemExit('Numeric relation production integration missing; controller never applies patches')
    for name in ['relation_keys_test.go','relation_keys_api_test.go']:
        if not (pkg/'internal/checker'/name).is_file():
            raise SystemExit('Focused numeric relation test missing: '+name)
    env = dict(os.environ, PATH=str(pathlib.Path(args.go).parent)+':'+os.environ['PATH'], GOFLAGS='', CGO_ENABLED='1')
    results = []; result_lock = threading.Lock()
    def capture(label):
        js = 'import {captureGoSources} from "./scripts/build-provenance.mjs"; console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
        value = json.loads(subprocess.check_output(['node','--input-type=module','-e',js], cwd=root))
        (output/(label+'.json')).write_text(json.dumps(value, indent=2)+'\n')
        return value
    def revision(path):
        return subprocess.check_output(['git','rev-parse','HEAD'],cwd=path,text=True).strip()
    fixture_revisions = {'typescript_go':revision(root/'upstream/typescript-go'), 'typescript':revision(root/'upstream/TypeScript')}
    expected = {'typescript_go':'2bd066d87f5bafd315be9f40889d0a60b9e58e0b','typescript':'4d4f005c8541e0255a9d8791205fdce326e462bc'}
    if fixture_revisions != expected:
        raise SystemExit('Pinned fixture revisions changed; review before running conformance')
    before = capture('source-before')
    if before['sha256'] != args.expected_source:
        raise SystemExit('Source digest differs from explicit parent-approved expected digest; no tests started')
    def run(name, command, cwd=pkg, overrides=None):
        run_env = env | dict(overrides or {})
        stdout = output/(name+'.jsonl'); stderr = output/(name+'.stderr')
        with stdout.open('w') as out, stderr.open('w') as err:
            process = subprocess.run(command, cwd=cwd, env=run_env, stdout=out, stderr=err)
        result = {'name':name,'command':command,'cwd':str(cwd),'environment':{k:run_env.get(k) for k in ['GOFLAGS','CGO_ENABLED','GOARCH','GOOS']},'exit_code':process.returncode,'stdout':str(stdout),'stderr':str(stderr),'stdout_sha256':hashlib.sha256(stdout.read_bytes()).hexdigest(),'stderr_sha256':hashlib.sha256(stderr.read_bytes()).hexdigest()}
        (output/(name+'.exit')).write_text(str(process.returncode)+'\n')
        with result_lock:
            results.append(result)
            (output/'process-results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(name, process.returncode, flush=True)
        return process.returncode
    focus = '^TestRelationKeys?(OrdinaryBoundariesMatchLegacy|GenericNormalizationMatchesLegacy|FallbackUsesAllHashBitsAndCheckerLifetime|PreserveMaybeStackCacheFlagsAndSize|RecursiveGenericAssignmentsAndDiagnostics|ColdRecursiveConstraints|RepeatedFailureDiagnosticsKeepUsePositions)$'
    codes = []
    try:
        codes.append(run('focused',[args.go,'test','-json','./internal/checker','-run',focus,'-count=1']))
        if not any(codes):
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(run,'checkptr',[args.go,'test','-json','-gcflags=all=-d=checkptr=2','./internal/checker','-run',focus,'-count=1']),pool.submit(run,'race',[args.go,'test','-json','-race','./internal/checker','-run',focus,'-count=1'])]
                codes += [f.result() for f in jobs]
        if not any(codes):
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(run,'root-npm',['npm','test'],root,{'GOFLAGS':'-json'}),pool.submit(run,'conformance',[args.go,'test','-json','./internal/testrunner','-run','^TestSubmodule$','-parallel','4','-timeout','30m'])]
                codes += [f.result() for f in jobs]
    finally:
        after = capture('source-after')
        report = summarize(output, results)
        report.update({'schema_version':1,'toolchain':subprocess.check_output([args.go,'version'],text=True).strip(),'fixture_revisions':fixture_revisions,'source_before':{k:before[k] for k in ['revision','dirty','sha256','digestAlgorithm']},'source_after':{k:after[k] for k in ['revision','dirty','sha256','digestAlgorithm']},'source_unchanged':before['sha256']==after['sha256'],'source_scope':'Complete captureGoSources manifest, including cmd/internal/scripts, go.mod/go.sum/package.json, build-provenance helper and untracked/ignored sources. Captures numeric relation packing/interner, consumers, and tests along with all local compiler source.','source_file_count':len(before['files']),'processes':results,'expected_source_sha256':args.expected_source,'coverage_limits':['Focused normal/race/checkptr select seven top-level numeric relation tests and two cold-direction subtests.','Race mode instruments actual interner and checker calls, but these tests do not deliberately run unsynchronized concurrent writes to one checker.','Flag/container tests cover overflow flag storage and accounting, not actual complexity/stack overflow generation or cached-overflow diagnostic reporting.','Cold recursive-constraint API cases exercise fresh and warm behavior; exact nested getRelationKey reentry count is not instrumented.','Root npm test covers ten packages; pinned conformance unsupported and partial output skips are reported separately.','Native CLI/API/parallel emit gates belong to the parent; no noninstrumented binary is claimed as race validation.','No durations are performance measurements.']})
        (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
        print('terminal source_unchanged=',report['source_unchanged'],flush=True)
    return 1 if any(codes) or not report['source_unchanged'] or report['validation_incomplete'] else 0

def summarize(output, runs):
    summaries = {}; incomplete = len(runs)!=5
    for run in runs:
        records = []; reasons = collections.defaultdict(list); package_status = {}; cached = set()
        with open(run['stdout']) as stream:
            for line in stream:
                if not line.startswith('{'): continue  # npm script headers
                event = json.loads(line)
                test = event.get('Test')
                if event['Action'] in ['pass','skip','fail']:
                    if test: records.append(event)
                    else: package_status[event['Package']] = event['Action']
                elif event['Action']=='output':
                    text = event.get('Output','')
                    if re.search(r'\.go:\d+: ',text): reasons[test].append(text)
                    if '(cached)' in text: cached.add(event['Package'])
        counts = collections.Counter(e['Action'] for e in records)
        tops = [e for e in records if '/' not in e['Test']]
        value = {'test_records':dict(counts),'top_level_records':dict(collections.Counter(e['Action'] for e in tops)),'passing_top_level_tests':[e['Test'] for e in tops if e['Action']=='pass'],'package_status':package_status,'cached_packages':sorted(cached)}
        if run['name'] in ['focused','checkptr','race']:
            if len(tops)!=7 or len(package_status)!=1 or counts['pass']!=9 or counts['skip'] or counts['fail']: incomplete=True
        if run['name']=='root-npm':
            if len(package_status)!=10: incomplete=True
            value['scope']='Exact current root npm test alias; actual package results above are authoritative. Expected current alias has ten Go packages.'
        if run['name']=='conformance':
            parents = [e for e in records if e['Test'].startswith('TestSubmodule/') and e['Test'].count('/')==1]
            partial = [e for e in records if e['Action']=='skip' and e['Test'].count('/')>1]
            partial_parents = {e['Test'].rsplit('/',1)[0] for e in partial}
            pc = collections.Counter(e['Action'] for e in parents)
            passed_parents = {e['Test'] for e in parents if e['Action']=='pass'}
            def reason(e):
                lines = reasons[e['Test']]
                for line in lines:
                    m = re.search(r'\.go:\d+: (.*)',line)
                    if m: return m.group(1).strip()
                return ''.join(lines).strip()
            categories = collections.Counter()
            for e in parents:
                if e['Action']!='skip':continue
                text = reason(e)
                for prefix in ['unsupported baseUrl','unsupported outFile']:
                    if text.startswith(prefix):text=prefix;break
                categories[text]+=1
            value['source_configuration_cases']={'total':len(parents),'fully_checked':len(passed_parents-partial_parents),'partially_checked':len(passed_parents&partial_parents),'unsupported_skipped':pc['skip'],'failed':pc['fail']}
            value['skip_categories']=dict(categories)
            value['partial_output_skips']=[{'test':e['Test'],'reason':reason(e)} for e in partial]
            value['failed_tests']=[e['Test'] for e in records if e['Action']=='fail']
            if not parents or not package_status:incomplete=True
        summaries[run['name']]=value
    return {'suites':summaries,'validation_incomplete':incomplete}

if __name__=='__main__': sys.exit(main())
