"""Exploratory worker scaling on the retained production binary; run in isolation."""
from pathlib import Path
import hashlib, json, os, signal, statistics, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[3]
BINARY = ROOT / 'packages/tsc-go/dist/tsc-go'
BINARY_SHA = '9017fa9abe7add6cadf8cefffca2aea161938b63aeac46ed8d226d7dca916d2a'
SIDECAR_SHA = '5164f58805236585d39258604fb12e274475039d04fd3efd5b8572d84c2cf287'
SOURCE_SHA = 'b50f489f20634bf3570a18d0fcc5cf811036fbcefe2a5ea481b193f848768445'
# Balanced positions and immediate predecessors; every count occurs once/round.
ORDERS = [[1, 2, 8, 4], [2, 4, 1, 8], [4, 8, 2, 1], [8, 1, 4, 2]]
FORMAT = '{"userSeconds":%U,"systemSeconds":%S,"peakRssKiB":%M,"exitStatus":%x}'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse_resources(text):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            assert k not in result
            result[k] = v
        return result
    x = json.loads(text, object_pairs_hook=unique)
    assert set(x) == {'userSeconds', 'systemSeconds', 'peakRssKiB', 'exitStatus'}
    assert type(x['exitStatus']) is int and x['exitStatus'] == 0
    assert type(x['peakRssKiB']) is int and x['peakRssKiB'] > 0
    for k in ['userSeconds', 'systemSeconds']:
        assert type(x[k]) in (int, float) and 0 <= x[k] < float('inf')
    return x

def summarize(runs):
    result = {}
    for workers in [1, 2, 4, 8]:
        rows = [x for x in runs if x['workers'] == workers and x['phase'] == 'timed']
        assert len(rows) == 4
        result[str(workers)] = {
            'wallMedianMs': statistics.median(x['wallMs'] for x in rows),
            'cpuMedianSeconds': statistics.median(x['resources']['userSeconds'] + x['resources']['systemSeconds'] for x in rows),
            'rssMedianKiB': statistics.median(x['resources']['peakRssKiB'] for x in rows),
        }
    return result

def main():
    assert len(sys.argv) == 2, 'Supply a new output directory'
    output = Path(sys.argv[1]).resolve(); output.mkdir()
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(('TSC_', 'TS_GO_', 'SCRIPTC_', 'MIMALLOC_', 'MI_', 'GODEBUG_')) or key in ['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','GOCOVERDIR','LD_PRELOAD','CPUPROFILE','HEAPPROFILE']:
            env.pop(key)
    env['TSC_TS_LIB_DIR'] = str(ROOT / 'upstream/typescript-go/internal/bundled/libs')
    time_sha = sha('/usr/bin/time')
    version = subprocess.check_output(['/usr/bin/time','--version'],env=env,text=True)
    assert 'GNU' in version
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    sources_js = 'import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(captureGoSources(process.cwd()+"/packages/tsc-go").sha256)'
    def verify():
        assert sha(BINARY) == BINARY_SHA and sha(str(BINARY)+'.provenance.json') == SIDECAR_SHA
        assert sha('/usr/bin/time') == time_sha
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() == head
        assert subprocess.check_output(['node','--input-type=module','-e',sources_js],cwd=ROOT,env=env,text=True).strip() == SOURCE_SHA
    verify()
    report = {'status':'running','head':head,'binarySha256':BINARY_SHA,'sidecarSha256':SIDECAR_SHA,'sourceSha256':SOURCE_SHA,'controllerSha256':sha(__file__),'timeSha256':time_sha,'timeVersion':version,'orders':ORDERS,'cpuAffinity':sorted(os.sched_getaffinity(0)), 'scope':'Same production binary, fresh processes, warm filesystem. Default runtime settings, explicit checker count only. Four balanced rounds after one warmup/count. Exploratory scaling, not an adoption gate or native comparison. GNU time CPU precision is 0.01 seconds; wrapper-inclusive wall uses monotonic nanoseconds. RSS is command peak, not aggregate tree peak. No allocation counts measured.','projects':[]}
    def save(): (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def interrupt(sig, frame): raise KeyboardInterrupt(str(sig))
    for sig in [signal.SIGTERM, signal.SIGINT]: signal.signal(sig, interrupt)
    save()
    try:
        for group in ['small','large']:
            reference = ROOT / f'benchmarks/results/native-project-inlining/{group}.json'
            prior = json.loads(reference.read_text()); assert prior['status'] == 'passed'
            for p in prior['projects']:
                def inputs():
                    assert sha(Path(p['cwd']) / p['args'][1]) == p['configSha256']
                    for item in p['preflight']['candidate']['inputs']:
                        assert sha(Path(p['cwd']) / item['file']) == item['sha256']
                inputs(); verify()
                assert '--checkers' not in p['args'] and '--extendedDiagnostics' not in p['args']
                project = {'name':p['name'],'reference':str(reference),'referenceSha256':sha(reference),'inputCount':p['preflight']['candidate']['fileCount'],'runs':[]}
                report['projects'].append(project); save()
                directory = output / p['name']; directory.mkdir()
                for round_no, order in enumerate([[1,2,4,8], *ORDERS]):
                    for workers in order:
                        prefix = directory / f'{round_no}-{workers}'
                        resource = prefix.with_suffix('.resources.json')
                        args = [*p['args'], '--checkers', str(workers)]
                        command = ['/usr/bin/time','--quiet','--output',str(resource),'--format',FORMAT,'--',str(BINARY),*args]
                        with prefix.with_suffix('.stdout').open('xb') as a, prefix.with_suffix('.stderr').open('xb') as b:
                            start = time.monotonic_ns()
                            child = subprocess.Popen(command,cwd=p['cwd'],env=env,stdout=a,stderr=b,start_new_session=True)
                            try: code = child.wait(timeout=300)
                            finally:
                                try: os.killpg(child.pid,signal.SIGKILL)
                                except ProcessLookupError: pass
                                child.wait()
                            wall = (time.monotonic_ns()-start)/1e6
                        assert code == 0
                        assert prefix.with_suffix('.stdout').read_bytes() == b'' and prefix.with_suffix('.stderr').read_bytes() == b''
                        row = {'round':round_no,'phase':'warmup' if round_no==0 else 'timed','workers':workers,'command':command,'cwd':p['cwd'],'wallMs':wall,'resources':parse_resources(resource.read_text()),'files':{f.name:sha(f) for f in [resource,prefix.with_suffix('.stdout'),prefix.with_suffix('.stderr')]}}
                        project['runs'].append(row); save()
                        print(p['name'],round_no,workers,round(wall,2),flush=True)
                inputs(); verify(); project['summary'] = summarize(project['runs']); save()
        assert sha(__file__) == report['controllerSha256']
        report['status'] = 'passed'
    except BaseException as error:
        report['status'] = 'failed'; report['error'] = repr(error); raise
    finally: save()

if __name__ == '__main__': main()
