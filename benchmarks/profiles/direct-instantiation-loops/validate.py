from pathlib import Path
import hashlib,json,os,subprocess,sys
p=Path(__file__).resolve().parent;r=p.parents[2];prefix='baseline-' if '--baseline' in sys.argv else '';overlay=p/(prefix+'overlay.json')
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources=json.loads(overlay.read_text())['Replace'];frozen={k:sha(v) for k,v in sources.items()}
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64','GORACE']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
report={'status':'running','sources':frozen,'controllerSha256':sha(__file__),'results':[]};path=p/(prefix+'validation.json');assert not path.exists()
def save():path.write_text(json.dumps(report,indent=2)+'\n')
try:
 for name,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
  cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(overlay),*flags,'./internal/checker','-run','^TestDirectInstantiation(Type|Symbol|Signature|Index)Histories$']
  out=p/(prefix+name+'.stdout');err=p/(prefix+name+'.stderr')
  with out.open('x') as a,err.open('x') as b:code=subprocess.run(cmd,cwd=r/'packages/tsc-go',env=env,stdout=a,stderr=b).returncode
  events=[json.loads(l) for l in out.read_text().splitlines()]
  passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
  observations=[json.loads(e['Output'].split('OBSERVED ',1)[1]) for e in events if 'OBSERVED ' in e.get('Output','')]
  ok=code==0 and set(passed)=={'TestDirectInstantiationTypeHistories','TestDirectInstantiationIndexHistories','TestDirectInstantiationSymbolHistories','TestDirectInstantiationSignatureHistories'} and len(passed)==4 and not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
  report['results'].append({'name':name,'command':cmd,'exitCode':code,'passed':passed,'ok':ok,'observations':observations,'stdoutSha256':sha(out),'stderrSha256':sha(err)});save();assert ok
  assert frozen=={k:sha(v) for k,v in sources.items()}
  print(prefix+name,'passed',flush=True)
 report['status']='passed'
except BaseException as e:report['status']='failed';report['error']=repr(e);raise
finally:save()
