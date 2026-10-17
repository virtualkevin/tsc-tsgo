from pathlib import Path
import subprocess,os,json,re,hashlib,signal
r=Path('/home/dev/tssss/tsc-tsgo');p=Path('/tmp/tsc-indexed-integration');out=p/'control-native';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();build=json.loads((p/'control-build.json').read_text());bin=r/'packages/tsc-go/dist/tsc-go-symbol-handles'
paths=[bin,Path(str(bin)+'.provenance.json'),r/'packages/tsc-ts/dist/tsc-original',r/'packages/tsgo/dist/tsgo',r/'node_modules/@scriptc/cli-linux-x64-gnu/dist/lib/typescript/lib/tsc']
frozen={str(path):sha(path) for path in paths};assert frozen[str(bin)]==build['binarySha256'];assert frozen[str(paths[1])]==build['sidecarSha256'];assert frozen[str(paths[2])]=='525c0fe92b231e13ce225687929a606b1d7d47851216cc10d4e2b91dfdcd0bb4';assert frozen[str(paths[3])]=='b7b9a43499f3b54a63d4901b2c5f05589ebbadb88c21bd8d174773be00502e1a'
env=os.environ.copy();cleared=[]
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['SHOW_FAILURES','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','NODE_OPTIONS','LD_PRELOAD']:
  cleared.append(k);env.pop(k,None)
env.update(TSC_GO_CANDIDATE=str(bin),TSC_GO_BASELINE=str(paths[2]),TSC_TS_BIN=str(bin))
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def capture():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=r,env=env,text=True))
before=capture();assert before['sha256']==build['sourceSha256'];child=None
report={'variant':'handle-only control','controllerSha256':sha(__file__),'sourceSha256':before['sha256'],'head':before['revision'],'binaryAndComparatorHashes':frozen,'clearedEnvironmentNames':cleared,'explicitEnvironment':{k:env[k] for k in ['TSC_GO_CANDIDATE','TSC_GO_BASELINE','TSC_TS_BIN']},'runs':[],'passed':False,'limits':['Normal CLI validation, not race-instrumented CLI coverage or workload timing.','Runs may overlap other non-performance validation; elapsed times are not benchmark data.','Source and binary identities checked; external dependency contents are not fully hashed.']}
def interrupt(signum,frame):raise KeyboardInterrupt('signal '+str(signum))
for signum in [signal.SIGINT,signal.SIGTERM]:signal.signal(signum,interrupt)
try:
 for name,cwd,files,expected in [('parity',r,['packages/tsc-go/tests/parity.mjs'],80),('integration',r/'packages/tsc-ts',['tests/api.test.mjs','tests/parallel-emit.test.mjs','tests/projects.test.mjs','tests/tsc-project.test.mjs'],12)]:
  command=['node','--test','--test-reporter=spec',*files];log=out/(name+'.log')
  with log.open('w') as f:
   child=subprocess.Popen(command,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   try:code=child.wait(timeout=900)
   finally:
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait();child=None
  text=re.sub(r'\x1b\[[0-9;]*m','',log.read_text());counts={m[0]:int(m[1]) for m in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}
  ok=code==0 and counts=={'tests':expected,'pass':expected,'fail':0,'cancelled':0,'skipped':0,'todo':0};report['runs'].append({'name':name,'command':command,'cwd':str(cwd),'exitCode':code,'counts':counts,'passed':ok,'logSha256':sha(log)});print(name,code,ok,flush=True);assert ok,'suite failed'
  after=capture();assert after['sha256']==before['sha256'] and after['revision']==before['revision'];assert all(sha(path)==h for path,h in frozen.items())
 report['passed']=len(report['runs'])==2;report['sourceAndBinariesUnchanged']=True
except BaseException as e:report['error']=str(e)
finally:
 (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('terminal passed='+str(report['passed']),flush=True)
raise SystemExit(0 if report['passed'] else 1)
