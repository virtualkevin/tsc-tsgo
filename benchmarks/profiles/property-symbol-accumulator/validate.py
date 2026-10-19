from pathlib import Path
import hashlib,json,os,subprocess
P=Path(__file__).resolve().parent;R=P.parents[2]
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources={str(f):sha(f) for f in (P/'staged').glob('*.go')}
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
report={'passed':False,'sources':sources,'runs':[]}
try:
 for variant in ['baseline','candidate']:
  for mode,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
   name=variant+'-'+mode;cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(P/(variant+'-overlay.json')),*flags,'./internal/checker','-run','^(TestPropertyAccumulatorQueryOrder|TestUnionPropertyCache)']
   with (P/(name+'.stdout')).open('x') as a,(P/(name+'.stderr')).open('x') as b:code=subprocess.run(cmd,cwd=R/'packages/tsc-go',env=env,stdout=a,stderr=b).returncode
   events=[json.loads(l) for l in (P/(name+'.stdout')).read_text().splitlines()];passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
   ok=code==0 and len(passed)==8 and not any(e.get('Action') in ['fail','skip'] for e in events)
   report['runs'].append(dict(name=name,command=cmd,exitCode=code,passed=ok,tests=passed));print(name,ok,flush=True)
   assert ok,name
   assert sources=={str(f):sha(f) for f in (P/'staged').glob('*.go')}
 report['passed']=True
except BaseException as e:report['error']=repr(e);raise
finally:(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
