from pathlib import Path
import hashlib,json,os,re,signal,subprocess
root=Path(__file__).resolve().parents[3];out=Path('/tmp/tsc-structured-call-data/instrumented');out.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','NODE_OPTIONS','LD_PRELOAD']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def capture():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,env=env,text=True))
baseline=root/'packages/tsc-ts/dist/tsc-original'
assert sha(baseline)=='525c0fe92b231e13ce225687929a606b1d7d47851216cc10d4e2b91dfdcd0bb4'
before=capture();assert before['sha256']=='dfadc4329383b5acb32127c9bdf14295a5cd94e113894d4c9cbb34d32a12d3d9'
report={'passed':False,'sourceSha256':before['sha256'],'head':before['revision'],'controllerSha256':sha(__file__),'runs':[]}
def interrupt(s,f):raise KeyboardInterrupt(str(s))
for s in [signal.SIGTERM,signal.SIGINT]:signal.signal(s,interrupt)
def run(command,cwd,environment,path):
 with path.open('w') as log:
  child=subprocess.Popen(command,cwd=cwd,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:return child.wait(timeout=2400)
  finally:
   try:os.killpg(child.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   child.wait()
try:
 for mode,flag in [('race','-race'),('checkptr','-gcflags=all=-d=checkptr=2')]:
  binary=out/('tsc-go-'+mode);build=['/tmp/tsc-toolchains/go/bin/go','build',flag,'-trimpath','-o',str(binary),'./cmd/tsgo'];buildlog=out/(mode+'-build.log')
  code=run(build,root/'packages/tsc-go',env,buildlog);assert code==0,mode+' build'
  digest=sha(binary);command=['node','--test','--test-reporter=spec','packages/tsc-go/tests/parity.mjs'];log=out/(mode+'-parity.log')
  code=run(command,root,env|{'TSC_GO_CANDIDATE':str(binary),'TSC_GO_BASELINE':str(root/'packages/tsc-ts/dist/tsc-original')},log)
  text=re.sub(r'\x1b\[[0-9;]*m','',log.read_text());counts={m[0]:int(m[1]) for m in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}
  ok=code==0 and counts=={'tests':80,'pass':80,'fail':0,'cancelled':0,'skipped':0,'todo':0}
  report['runs'].append(dict(mode=mode,buildCommand=build,command=command,buildLogSha256=sha(buildlog),binarySha256=digest,logSha256=sha(log),exitCode=code,counts=counts,passed=ok));(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(mode,ok,flush=True);assert ok
  after=capture();assert (after['sha256'],after['revision'])==(before['sha256'],before['revision']);assert sha(binary)==digest;assert sha(baseline)=='525c0fe92b231e13ce225687929a606b1d7d47851216cc10d4e2b91dfdcd0bb4'
 report['passed']=True
except BaseException as e:report['error']=repr(e)
finally:(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
