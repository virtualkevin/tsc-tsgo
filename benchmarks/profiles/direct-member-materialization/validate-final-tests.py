"""Full staged Go-side validation; keeps source, HEAD and oracle pins fixed."""
import gzip,importlib.util,json,os,signal,subprocess,sys
sys.dont_write_bytecode=True
from final_common import *
verify();assert json.loads((PROFILE/'validation.json').read_text())['passed'];out=OUT/'tests-02';out.mkdir(parents=True,exist_ok=False)
report_path=PROFILE/'final-tests.json';assert not report_path.exists()
helper=ROOT/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py'
spec=importlib.util.spec_from_file_location('conformance_summary',helper);summary_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(summary_module)
pins={'TypeScript':'4d4f005c8541e0255a9d8791205fdce326e462bc','typescript-go':'2bd066d87f5bafd315be9f40889d0a60b9e58e0b'}
def verify_pins():
 assert {name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT/'upstream'/name,text=True).strip() for name in pins}==pins
verify_pins()
focused=['./internal/checker','-run','^Test(DirectMaterialization|Pending)']
root_packages=['./internal/parser','./internal/printer','./internal/core','./internal/ast','./internal/bundled','./internal/scanner','./internal/compiler','./internal/checker','./cmd/tsgo','./internal/execute','./internal/execute/build','./internal/execute/watchmanager','./internal/binder','./internal/api/encoder']
phases=[('checkptr',['-gcflags=all=-d=checkptr=2',*focused],1),('root',root_packages,14),('services',['./internal/api/...','./internal/ls/...'],7),('conformance',['./internal/testrunner','-run','^TestSubmodule$','-parallel','4'],1)]
report={'scope':'Frozen overlay focused/root/services and complete pinned conformance validation. CLI/API/emit parity and performance tracked separately.','passed':False,'freezeSha256':sha(PROFILE/'final-freeze.json'),'commonSha256':sha(PROFILE/'final_common.py'),'controllerSha256':sha(__file__),'summaryHelperSha256':sha(helper),'pins':pins,'runs':[]}
def save():report_path.write_text(json.dumps(report,indent=2)+'\n')
def interrupt(signum,frame):raise KeyboardInterrupt(str(signum))
for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,interrupt)
try:
 for name,args,package_count in phases:
  verify();verify_pins();command=[GO,'test','-overlay',str(OVERLAY),'-json',*args,'-count=1','-timeout','30m']
  stdout=out/(name+'.jsonl');stderr=out/(name+'.stderr')
  with stdout.open('w') as a,stderr.open('w') as b:
   child=subprocess.Popen(command,cwd=MODULE,env=ENV,stdout=a,stderr=b,start_new_session=True)
   try:code=child.wait(timeout=2400)
   finally:
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait()
  run={'name':name,'command':command,'exit_code':code,'stdout':str(stdout),'stderr':str(stderr),'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr)}
  if name=='conformance':
   summary=summary_module.summarize_run(run)
   ok=code==0 and not summary['integrity_errors'] and summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
  else:
   events=[json.loads(line) for line in stdout.read_text().splitlines()]
   terminal=[e for e in events if e['Action'] in ['pass','fail','skip']];tests=[e for e in terminal if e.get('Test')];packages=[e for e in terminal if 'Test' not in e];top=[e['Test'] for e in tests if '/' not in e['Test']]
   allowed_empty='github.com/microsoft/typescript-go/internal/ls/change'
   ok=code==0 and len(packages)==package_count and all(e['Action']=='pass' for e in tests) and all(e['Action']=='pass' or (name=='services' and e['Action']=='skip' and e['Package']==allowed_empty and any(v.get('Package')==allowed_empty and '[no test files]' in v.get('Output','') for v in events)) for e in packages)
   if name in ['normal','race','checkptr']:ok=ok and len(tests)==21 and len(top)==16
   if name=='root':ok=ok and len(tests)==21182 and len(top)==251
   if name=='services':ok=ok and len(tests)==219 and len(top)==60
   summary={'tests':len(tests),'topLevelTests':top,'packages':{e['Package']:e['Action'] for e in packages}}
  archive={}
  for raw in [stdout,stderr]:
   target=PROFILE/'final-test-logs'/(raw.name+'.gz');target.parent.mkdir(exist_ok=True)
   with target.open('wb') as file:
    with gzip.GzipFile(filename='',mode='wb',fileobj=file,mtime=0) as zipped:zipped.write(raw.read_bytes())
   assert gzip.decompress(target.read_bytes())==raw.read_bytes();archive[target.name]={'sha256':sha(target),'rawSha256':sha(raw)}
  run.update(passed=ok,summary=summary,archive=archive);report['runs'].append(run);save();print(name,code,ok,flush=True);assert ok,name
  verify();verify_pins()
 report['passed']=True
except BaseException as error:report['error']=repr(error)
finally:save()
raise SystemExit(0 if report['passed'] else 1)
