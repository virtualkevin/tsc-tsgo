from pathlib import Path
import os,json,hashlib,subprocess,signal
from counts import validate
root=Path(__file__).resolve().parents[3]; out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def source():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True))
before=source(); assert before['sha256']=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
baseline=root/'packages/tsc-go/dist/tsc-go-property-relation-snapshot';candidate=Path('/tmp/tsc-property-view-boundaries')
sidecar=Path(str(baseline)+'.provenance.json')
assert sha(sidecar)=='8fbdc94867cf7da5335d8209b22a9da188b2537d3f479b0327d4beb46a3c0b77'
assert sha(baseline)=='0cee0116847b25ac1cc87ffc1613a77971659b8aa92fc7d3da8995d542439022'
validation=json.loads((out/'validation.json').read_text());assert validation['status']=='passed' and [x['name'] for x in validation['results']]==['normal','race','checkptr']
assert all(x['exitCode']==0 and len(x['passed'])==16 for x in validation['results'])
overlay=json.loads((out/'overlay.json').read_text())['Replace'];frozen={k:sha(v) for k,v in overlay.items()}
assert validation['sources']==frozen
build=json.loads((out/'build.json').read_text());assert build['exitCode']==0 and sha(candidate)==build['binarySha256'] and build['overlaySources']==frozen
report={'status':'running','scope':'Diagnostic property-view coverage on rejected candidate, with uninstrumented candidate and observer-disabled controls. No timing, liveness or speedup claim.', 'baseHead':before['revision'],'baseSource':before['sha256'],'baselineSha256':sha(baseline),'baselineSidecarSha256':sha(sidecar),'candidateSha256':sha(candidate),'overlaySources':frozen,'controllerSha256':sha(__file__),'countsValidatorSha256':sha(out/'counts.py'),'validationSha256':sha(out/'validation.json'),'buildReportSha256':sha(out/'build.json'),'runs':[]}
reportPath=out/'report.json';assert not reportPath.exists()
env=os.environ.copy();removed=[]
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOEXPERIMENT','NODE_OPTIONS','LD_PRELOAD','GOCOVERDIR','GOTRACEBACK','MALLOC_CONF','MALLOC_ARENA_MAX']:
  removed.append(k);env.pop(k,None)
env['TSC_TS_LIB_DIR']=str(root/'upstream/typescript-go/internal/bundled/libs');report['removedEnvironmentNames']=sorted(removed)
def save():reportPath.write_text(json.dumps(report,indent=2)+'\n')
def inputs(p):
 assert sha(Path(p['cwd'])/p['args'][1])==p['configSha256']
 for f in p['preflight']['candidate']['inputs']:assert sha(Path(p['cwd'])/f['file'])==f['sha256']
child=None
def stop_child():
 if child is not None and child.poll() is None:
  os.killpg(child.pid,signal.SIGTERM)
  try:child.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
def cancel(sig,frame):
 stop_child();raise SystemExit(128+sig)
for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,cancel)
save()
try:
 for group in ['small','large']:
  ref=root/f'benchmarks/results/native-node-pointer/{group}.json';old=json.loads(ref.read_text());assert old['status']=='passed'
  for p in old['projects']:
   inputs(p);work=out/p['name'];work.mkdir(exist_ok=False)
   for mode in ['baseline','disabled','enabled']:
    binary=baseline if mode=='baseline' else candidate
    runenv=env|({'TSC_GO_PROPERTY_VIEW_CENSUS':str(work/'census.json')} if mode=='enabled' else {})
    command=[str(binary),*p['args']]
    assert not any('trace' in a.lower() or 'pprof' in a.lower() for a in p['args'])
    with (work/(mode+'.stdout')).open('wb') as a,(work/(mode+'.stderr')).open('wb') as b:
     child=subprocess.Popen(command,cwd=p['cwd'],env=runenv,stdout=a,stderr=b,start_new_session=True)
     try:code=child.wait(timeout=600)
     except BaseException:stop_child();raise
     finally:child=None
    assert code==0 and (work/(mode+'.stdout')).read_bytes()==b'' and (work/(mode+'.stderr')).read_bytes()==b'',(p['name'],mode,code)
    artifacts={};counts=None
    if mode=='enabled':
     f=work/'census.json';counts=validate(json.loads(f.read_text()))
     artifacts={'census.json':{'sha256':sha(f),'bytes':f.stat().st_size}}
    report['runs'].append({'project':p['name'],'mode':mode,'command':command,'cwd':p['cwd'],'reference':str(ref.relative_to(root)),'referenceSha256':sha(ref),'inputCount':len(p['preflight']['candidate']['inputs']),'exitStatus':code,'stdoutSha256':sha(work/(mode+'.stdout')),'stderrSha256':sha(work/(mode+'.stderr')),'artifacts':artifacts,'counts':counts});save();print(p['name'],mode,'passed',flush=True)
   inputs(p)
 assert sha(baseline)==report['baselineSha256'] and sha(candidate)==report['candidateSha256'] and sha(sidecar)==report['baselineSidecarSha256']
 after=source();assert (before['sha256'],before['revision'])==(after['sha256'],after['revision'])
 assert frozen=={k:sha(v) for k,v in overlay.items()};assert sha(__file__)==report['controllerSha256'];assert sha(out/'counts.py')==report['countsValidatorSha256']
 report['status']='passed'
except BaseException as e:report['status']='failed';report['error']=repr(e);raise
finally:stop_child();save()
