from pathlib import Path
import subprocess, os, json, hashlib, importlib.util, signal, sys
root=Path('/home/dev/tssss/tsc-tsgo');pkg=root/'packages/tsc-go';go='/tmp/tsc-toolchains/go/bin/go'
sys.dont_write_bytecode=True
def interrupt(signum, frame): raise KeyboardInterrupt('signal '+str(signum))
for signum in [signal.SIGINT, signal.SIGTERM]: signal.signal(signum, interrupt)
variant=sys.argv[1]; expected_source=sys.argv[2];out=Path('/tmp/tsc-parser-interner')/variant;out.mkdir(exist_ok=False)
helper=root/'benchmarks/profiles/prehashed-relations-512/validation-controller/validate.py'
spec=importlib.util.spec_from_file_location('old_validator',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64','GOCOVERDIR']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local',PATH=str(Path(go).parent)+':'+env.get('PATH',''))
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
def capture():return json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,env=env,text=True))
def pins():return {n:subprocess.check_output(['git','rev-parse','HEAD'],cwd=root/'upstream'/n,text=True).strip() for n in ['TypeScript','typescript-go']}
expected_pins={'TypeScript':'4d4f005c8541e0255a9d8791205fdce326e462bc','typescript-go':'2bd066d87f5bafd315be9f40889d0a60b9e58e0b'}
before=capture();assert before['sha256']==expected_source;assert pins()==expected_pins
(out/'source-before.json').write_text(json.dumps(before,indent=2)+'\n')
expected=set()
report={'variant':variant,'sourceSha256':expected_source,'head':before['revision'],'controllerSha256':sha(__file__),'summaryHelperSha256':sha(helper),'expectedFocusedTests':sorted(expected),'pins':expected_pins,'runs':[],'passed':False,'scope':'Complete pinned conformance only; focused/root suites tracked separately; no workload timing claim.'}
try:
 runs=[('conformance',[go,'test','-json','./internal/testrunner','-run','^TestSubmodule$','-parallel','4','-count=1','-timeout','30m'],pkg,{})]
 for name,command,cwd,extra in runs:
  stdout=out/(name+'.jsonl');stderr=out/(name+'.stderr')
  with stdout.open('w') as o,stderr.open('w') as e:
   child=subprocess.Popen(command,cwd=cwd,env=env|extra,stdout=o,stderr=e,start_new_session=True)
   try:code=child.wait(timeout=2400)
   except BaseException:
    os.killpg(child.pid,signal.SIGKILL);child.wait();raise
  run={'name':name,'command':command,'exit_code':code,'stdout':str(stdout),'stderr':str(stderr),'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr)}
  if name in ['root-npm','conformance']:
   summary=mod.summarize_run(run);ok=code==0 and not summary['integrity_errors']
   if name=='conformance':ok=ok and summary['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
  else:
   events=[json.loads(l) for l in stdout.read_text().splitlines() if l.startswith('{')];terminal=[e for e in events if e['Action'] in ['pass','fail','skip']];tests=[e for e in terminal if e.get('Test')];packages=[e for e in terminal if not e.get('Test')]
   ok=code==0 and {e['Test'] for e in tests}==expected and len(tests)==len(expected) and len(packages)==3 and all(e['Action']=='pass' for e in terminal)
   summary={'tests':[{k:e[k] for k in ['Package','Test','Action']} for e in tests],'packages':{e['Package']:e['Action'] for e in packages}}
  run.update(summary=summary,passed=ok);report['runs'].append(run);(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(name,code,ok,flush=True)
  assert ok,'suite failed: '+name
  after=capture();assert after['sha256']==expected_source and after['revision']==before['revision'],'source changed'
 assert pins()==expected_pins
 report['passed']=len(report['runs'])==1;report['sourceAndPinsUnchanged']=True
except BaseException as e:report['error']=str(e)
finally:(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('terminal passed='+str(report['passed']),flush=True)
sys.exit(0 if report['passed'] else 1)
