"""Normal and instrumented CLI parity plus normal API/emit integration."""
import gzip,json,os,re,signal,subprocess,sys
sys.dont_write_bytecode=True
from final_common import *
focused=json.loads((PROFILE/'validation.json').read_text());assert focused['passed']
assert focused['sources']=={str(Path(v)):sha(v) for v in json.loads(OVERLAY.read_text())['Replace'].values()}
assert [x['name'] for x in focused['runs']]==[v+'-'+m for v in ['baseline','candidate'] for m in ['normal','race','checkptr']]
assert all(x['exitCode']==0 and x['passed'] and len(x['tests'])==8 for x in focused['runs'])
verify();out=OUT/'cli-resumed';out.mkdir(parents=True,exist_ok=False)
normal=OUT/'tsc-property-symbol-accumulator'
build=json.loads((PROFILE/'build.json').read_text())
assert build['exitCode']==0 and build['sources']==FREEZE['sources'] and sha(normal)==build['binarySha256']
original=json.loads((PROFILE/'final-cli.json').read_text())
assert not original['passed'] and original['error']=="KeyboardInterrupt('15')"
assert [r['mode'] for r in original['runs']]==['normal','integration'] and all(r['passed'] for r in original['runs'])
assert original['controllerSha256']==sha(PROFILE/'validate-cli.py')

comparators=[ROOT/'packages/tsc-ts/dist/tsc-original',ROOT/'packages/tsgo/dist/tsgo',ROOT/'node_modules/@scriptc/cli-linux-x64-gnu/dist/lib/typescript/lib/tsc']
frozen={str(p):sha(p) for p in comparators};assert frozen[str(comparators[0])]=='525c0fe92b231e13ce225687929a606b1d7d47851216cc10d4e2b91dfdcd0bb4';assert frozen[str(comparators[1])]=='b7b9a43499f3b54a63d4901b2c5f05589ebbadb88c21bd8d174773be00502e1a'
report_path=PROFILE/'final-cli-resumed.json';assert not report_path.exists()
report={'scope':'Frozen overlay normal CLI/API/emit integration and race/checkptr CLI differential tests. Not workload timing or standard production build provenance.','passed':False,'freezeSha256':sha(PROFILE/'cli-freeze.json'),'controllerSha256':sha(__file__),'commonSha256':sha(PROFILE/'final_common.py'),'normalBuildSha256':sha(PROFILE/'build.json'),'comparators':frozen,'runs':[]}
for key in ['freezeSha256','commonSha256','normalBuildSha256','comparators']:
 assert report[key]==original[key],key
report['originalReportSha256']=sha(PROFILE/'final-cli.json')
report['runs']=list(original['runs'])
def save():report_path.write_text(json.dumps(report,indent=2)+'\n')
def interrupt(sig,frame):raise KeyboardInterrupt(str(sig))
for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,interrupt)
def run(command,cwd,environment,path):
 with path.open('w') as log:
  child=subprocess.Popen(command,cwd=cwd,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:return child.wait(timeout=2400)
  finally:
   try:os.killpg(child.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   child.wait()
def archive(path):
 target=PROFILE/'final-cli-logs'/('resumed-'+path.name+'.gz');target.parent.mkdir(exist_ok=True)
 with target.open('wb') as output:
  with gzip.GzipFile(filename='',mode='wb',fileobj=output,mtime=0) as zipped:zipped.write(path.read_bytes())
 assert gzip.decompress(target.read_bytes())==path.read_bytes()
 return {'file':target.name,'sha256':sha(target),'rawSha256':sha(path)}
try:
 for mode in ['race','checkptr']:
  verify();assert all(sha(p)==h for p,h in frozen.items())
  binary=normal;entry={'mode':mode}
  if mode in ['race','checkptr']:
   binary=out/('tsc-go-'+mode);flag='-race' if mode=='race' else '-gcflags=all=-d=checkptr=2'
   command=[GO,'build',flag,'-trimpath','-overlay',str(OVERLAY),'-o',str(binary),'./cmd/tsgo'];log=out/(mode+'-build.log');code=run(command,MODULE,ENV,log)
   entry.update(buildCommand=command,buildExitCode=code,buildLog=archive(log));assert code==0,mode+' build failed'
  digest=sha(binary)
  environment=ENV|{'TSC_GO_CANDIDATE':str(binary),'TSC_GO_BASELINE':str(comparators[0]),'TSC_TS_BIN':str(binary)}
  if mode=='integration':
   cwd=ROOT/'packages/tsc-ts';files=['tests/api.test.mjs','tests/parallel-emit.test.mjs','tests/projects.test.mjs','tests/tsc-project.test.mjs'];expected=12
  else:cwd=ROOT;files=['packages/tsc-go/tests/parity.mjs'];expected=80
  command=['node','--test','--test-reporter=spec',*files];log=out/(mode+'.log');code=run(command,cwd,environment,log)
  text=re.sub(r'\x1b\[[0-9;]*m','',log.read_text());counts={k:int(v) for k,v in re.findall(r'^(?:ℹ\s*)?(tests|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$',text,re.M)}
  ok=code==0 and counts=={'tests':expected,'pass':expected,'fail':0,'cancelled':0,'skipped':0,'todo':0}
  entry.update(command=command,cwd=str(cwd),binarySha256=digest,exitCode=code,counts=counts,log=archive(log),passed=ok);report['runs'].append(entry);save();print(mode,code,ok,flush=True);assert ok,mode
  verify();assert sha(binary)==digest and sha(normal)==build['binarySha256'];assert all(sha(p)==h for p,h in frozen.items())
 report['passed']=True
except BaseException as error:report['error']=repr(error)
finally:save()
raise SystemExit(0 if report['passed'] else 1)
