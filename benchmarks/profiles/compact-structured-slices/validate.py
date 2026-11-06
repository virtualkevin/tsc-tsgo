from pathlib import Path
import subprocess,os,json,hashlib,sys
p=Path(__file__).resolve().parent;r=p.parents[2];env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
baseline='--baseline' in sys.argv;prefix='baseline-' if baseline else '';overlay=p/(prefix+'overlay.json')
sources=json.loads(overlay.read_text())['Replace'];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();frozen={k:sha(v) for k,v in sources.items()}
expected={'TestCompactStructuredSliceAliases','TestCompactStructuredSignatureCapacity','TestCompactStructuredNilAndEmpty'}
report={'status':'running','sources':frozen,'controllerSha256':sha(__file__),'results':[]}
def save():(p/(prefix+'validation.json')).write_text(json.dumps(report,indent=2)+'\n')
try:
 for name,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
  cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(overlay),*flags,'./internal/checker','-run','^(TestCompactStructured|TestPending)']
  with (p/(prefix+name+'.stdout')).open('x') as a,(p/(prefix+name+'.stderr')).open('x') as b:code=subprocess.run(cmd,cwd=r/'packages/tsc-go',env=env,stdout=a,stderr=b).returncode
  records=[json.loads(x) for x in (p/(prefix+name+'.stdout')).read_text().splitlines()];passed=[x['Test'] for x in records if x.get('Action')=='pass' and 'Test' in x]
  ok=code==0 and expected<=set(passed) and not any(x.get('Action') in ['fail','skip','build-fail'] for x in records)
  report['results'].append({'name':name,'command':cmd,'exitCode':code,'passed':passed,'ok':ok,'stdoutSha256':sha(p/(prefix+name+'.stdout')),'stderrSha256':sha(p/(prefix+name+'.stderr'))});save()
  assert ok
  assert frozen=={k:sha(v) for k,v in sources.items()}
  print(prefix+name,'passed',flush=True)
 report['status']='passed'
except BaseException as error:report['status']='failed';report['error']=repr(error);raise
finally:save()
