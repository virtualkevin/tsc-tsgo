from pathlib import Path
import subprocess,os,json,hashlib,signal
r=Path('/home/dev/tssss/tsc-tsgo');out=Path('/tmp/tsc-reduction-small-pair/units');out.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
go='/tmp/tsc-toolchains/go/bin/go'
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def capture():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=r,env=env,text=True))
before=capture();assert before['sha256']=='c120f3fc891cad13d5ef4407195255d56307a299322c42ed242e59ccc3c4a199'
report={'sourceSha256':before['sha256'],'head':before['revision'],'controllerSha256':sha(__file__),'runs':[],'passed':False}
def interrupt(s,f):raise KeyboardInterrupt(str(s))
for s in [signal.SIGINT,signal.SIGTERM]:signal.signal(s,interrupt)
try:
 for name,args in [('race',['-race','./internal/checker','-run','Test(Lazy|SmallPair)']),('checkptr',['-gcflags=all=-d=checkptr=2','./internal/checker','-run','Test(Lazy|SmallPair)']),('root',['./internal/core','./internal/ast','./internal/bundled','./internal/scanner','./internal/compiler','./internal/checker','./cmd/tsgo','./internal/execute','./internal/execute/build','./internal/execute/watchmanager'])]:
  command=[go,'test','-json',*args,'-count=1','-timeout','20m'];stdout=out/(name+'.jsonl');stderr=out/(name+'.stderr')
  with stdout.open('w') as a,stderr.open('w') as b:
   child=subprocess.Popen(command,cwd=r/'packages/tsc-go',env=env,stdout=a,stderr=b,start_new_session=True)
   try:code=child.wait(timeout=1500)
   finally:
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait()
  events=[json.loads(x) for x in stdout.read_text().splitlines()];terminal=[e for e in events if e['Action'] in ['pass','skip','fail']];tests=[e for e in terminal if e.get('Test')];packages=[e for e in terminal if not e.get('Test')];top=[e['Test'] for e in tests if '/' not in e['Test']]
  ok=code==0 and all(e['Action']=='pass' for e in terminal) and len(packages)==(10 if name=='root' else 1) and len(top)>0
  if name!='root':ok=ok and len(tests)==128 and len(top)==8
  entry={'name':name,'command':command,'exitCode':code,'tests':len(tests),'topLevelTests':top,'packages':{e['Package']:e['Action'] for e in packages},'stdoutSha256':sha(stdout),'stderrSha256':sha(stderr),'passed':ok};report['runs'].append(entry)
  (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(name,code,ok,flush=True);assert ok
  after=capture();assert (after['sha256'],after['revision'])==(before['sha256'],before['revision'])
 report['passed']=len(report['runs'])==3
except BaseException as e:report['error']=repr(e)
finally:(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
