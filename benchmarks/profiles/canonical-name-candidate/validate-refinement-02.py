"""Validate a frozen staged overlay, archiving compressed raw test evidence."""
from pathlib import Path
import gzip,hashlib,json,os,signal,subprocess
profile=Path(__file__).resolve().parent
root=profile.parents[2]
module=root/'packages/tsc-go'
out=Path('/tmp/tsc-canonical-names/refinement-validation-02')
out.mkdir(parents=True,exist_ok=True)
assert not (profile/'refinement-validation-02.json').exists(), 'preserve completed/prior attempt reports'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((profile/'refinement-freeze-02.json').read_text())
def verify():
 overlay=json.loads((profile/'overlay.json').read_text())['Replace']
 actual={str(Path(k).relative_to(module)):sha(v) for k,v in overlay.items()}
 assert actual==freeze['sources']
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==freeze['head']
verify()
env=os.environ.copy()
for key in list(env):
 if key.startswith(('TSC_','TS_GO_','SCRIPTC_')) or key in ['GOFLAGS','GOEXPERIMENT','GODEBUG','GOGC','GOMEMLIMIT','GOMAXPROCS','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR']:
  env.pop(key,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
focused=['./internal/ast','./internal/parser','./internal/binder','./internal/checker','-run','^Test(CanonicalName|PendingMember)']
root_packages=['./internal/parser','./internal/printer','./internal/core','./internal/ast','./internal/bundled','./internal/scanner','./internal/compiler','./internal/checker','./cmd/tsgo','./internal/execute','./internal/execute/build','./internal/execute/watchmanager','./internal/binder','./internal/api/encoder']
phases=[('normal',focused,4),('race',['-race',*focused],4),('checkptr',['-gcflags=all=-d=checkptr=2',*focused],4),('root',root_packages,14)]
report={'scope':'Staged declaration/constant/syntax refinement validation; not full conformance, CLI/API/emit/services suite or performance evidence.','passed':False,'freezeSha256':sha(profile/'refinement-freeze-02.json'),'controllerSha256':sha(__file__),'runs':[]}
def save():(profile/'refinement-validation-02.json').write_text(json.dumps(report,indent=2)+'\n')
def interrupt(signum,frame):raise KeyboardInterrupt(str(signum))
for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,interrupt)
try:
 for name,args,count in phases:
  verify();command=['/tmp/tsc-toolchains/go/bin/go','test','-overlay',str(profile/'overlay.json'),'-json',*args,'-count=1','-timeout','20m']
  stdout=out/(name+'.jsonl');stderr=out/(name+'.stderr')
  assert not stdout.exists() and not stderr.exists(),name
  with stdout.open('w') as a,stderr.open('w') as b:
   child=subprocess.Popen(command,cwd=module,env=env,stdout=a,stderr=b,start_new_session=True)
   try:code=child.wait(timeout=1500)
   finally:
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait()
  events=[json.loads(line) for line in stdout.read_text().splitlines()]
  terminal=[e for e in events if e['Action'] in ['pass','fail','skip']]
  tests=[e for e in terminal if e.get('Test')];packages=[e for e in terminal if 'Test' not in e]
  ok=code==0 and all(e['Action']=='pass' for e in terminal) and len(packages)==count
  if name!='root':ok=ok and len(tests)==19 and sum('/' not in e['Test'] for e in tests)==17
  archive={}
  for raw in [stdout,stderr]:
   target=profile/'refinement-02-logs'/(raw.name+'.gz');target.parent.mkdir(exist_ok=True)
   with target.open('wb') as file:
    with gzip.GzipFile(filename='',mode='wb',fileobj=file,mtime=0) as compressed:compressed.write(raw.read_bytes())
   assert gzip.decompress(target.read_bytes())==raw.read_bytes()
   archive[target.name]={'sha256':sha(target),'rawSha256':sha(raw)}
  report['runs'].append({'name':name,'command':command,'exitCode':code,'passed':ok,'tests':len(tests),'topLevelTests':[e['Test'] for e in tests if '/' not in e['Test']],'packages':{e['Package']:e['Action'] for e in packages},'stdoutSha256':sha(stdout),'stderrSha256':sha(stderr),'archive':archive})
  save();print(name,code,ok,len(tests),flush=True);assert ok,name;verify()
 report['passed']=True
except BaseException as error:
 report['error']=repr(error)
finally:save()
raise SystemExit(0 if report['passed'] else 1)
