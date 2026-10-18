from pathlib import Path
import gzip,hashlib,importlib.util,json,os,signal,subprocess,sys
sys.dont_write_bytecode=True
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ('GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR','NODE_OPTIONS','LD_PRELOAD','SHOW_FAILURES'):env.pop(k,None)
go='/tmp/tsc-toolchains/go/bin/go'
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local',PATH=str(Path(go).parent)+':'+env.get('PATH',''))
overlay=p/'overlay.json';sources=json.loads(overlay.read_text())['Replace']
frozen={k:sha(v) for k,v in sources.items()}
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
base=json.loads((p/'base.json').read_text())
pins={'TypeScript':'4d4f005c8541e0255a9d8791205fdce326e462bc','typescript-go':'2bd066d87f5bafd315be9f40889d0a60b9e58e0b'}
def verify():
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==head
 assert frozen=={k:sha(v) for k,v in sources.items()}
 assert all(sha(m/k)==v for k,v in base.items())
 assert {k:subprocess.check_output(['git','rev-parse','HEAD'],cwd=r/'upstream'/k,text=True).strip() for k in pins}==pins
 js='import {captureGoSources} from "./scripts/build-provenance.mjs";const s=captureGoSources(process.cwd()+"/packages/tsc-go");console.log(s.sha256)'
 assert subprocess.check_output(['node','--input-type=module','-e',js],cwd=r,env=env,text=True).strip()=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
 assert sha(m/'dist/tsc-go')=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
verify()
helper=r/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py'
spec=importlib.util.spec_from_file_location('conformance_summary',helper);summary_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(summary_module)
root_packages=['./internal/'+x for x in ['parser','printer','core','ast','bundled','scanner','compiler','checker','execute','execute/build','execute/watchmanager','binder','api/encoder']]+['./cmd/tsgo']
phases=[('services',['./internal/api/...','./internal/ls/...'],7,219),('conformance',['./internal/testrunner','-run','^TestSubmodule$','-parallel','4'],1,None)]
report={'passed':False,'head':head,'sources':frozen,'pins':pins,'controllerSha256':sha(__file__),'helperSha256':sha(helper),'runs':[]}
output=p/'remaining-logs';output.mkdir(exist_ok=False)
def save():(p/'validation-remaining.json').write_text(json.dumps(report,indent=2)+'\n')
def interrupt(signum,frame):raise KeyboardInterrupt(str(signum))
for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,interrupt)
try:
 for name,args,expected_packages,expected_tests in phases:
  verify();cmd=[go,'test','-overlay',str(overlay),'-json',*args,'-count=1','-timeout','30m']
  stdout=output/(name+'.jsonl');stderr=output/(name+'.stderr')
  with stdout.open('x') as a,stderr.open('x') as b:
   child=subprocess.Popen(cmd,cwd=m,env=env,stdout=a,stderr=b,start_new_session=True)
   try:code=child.wait(timeout=2400)
   finally:
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait()
  run={'name':name,'command':cmd,'exit_code':code,'stdout':str(stdout),'stderr':str(stderr),'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr)}
  if name=='conformance':
   summary=summary_module.summarize_run(run)
   ok=code==0 and not summary['integrity_errors'] and summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
  else:
   events=[json.loads(x) for x in stdout.read_text().splitlines()]
   terminal=[x for x in events if x.get('Action') in ('pass','fail','skip')]
   tests=[x for x in terminal if 'Test' in x];packages=[x for x in terminal if 'Test' not in x]
   allowed_empty='github.com/microsoft/typescript-go/internal/ls/change'
   ok=code==0 and len(packages)==expected_packages and len(tests)==expected_tests and all(x['Action']=='pass' for x in tests) and all(x['Action']=='pass' or (name=='services' and x['Action']=='skip' and x['Package']==allowed_empty and any(e.get('Package')==allowed_empty and '[no test files]' in e.get('Output','') for e in events)) for x in packages)
   summary={'tests':len(tests),'topLevelTests':[x['Test'] for x in tests if '/' not in x['Test']],'packages':{x['Package']:x['Action'] for x in packages}}
  archive={}
  for raw in (stdout,stderr):
   target=raw.with_suffix(raw.suffix+'.gz')
   with target.open('xb') as file:
    with gzip.GzipFile(filename='',mode='wb',fileobj=file,mtime=0) as zipped:zipped.write(raw.read_bytes())
   assert gzip.decompress(target.read_bytes())==raw.read_bytes()
   archive[target.name]=sha(target)
  run.update(passed=ok,summary=summary,archive=archive);report['runs'].append(run);save();print(name,code,ok,flush=True)
  assert ok,name
  verify()
 report['passed']=True
except BaseException as error:report['error']=repr(error)
finally:save()
raise SystemExit(0 if report['passed'] else 1)
