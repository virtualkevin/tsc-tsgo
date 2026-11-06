from pathlib import Path
import hashlib,json,os,subprocess
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources={f.name:sha(f) for f in sorted((p/'prototype').iterdir()) if f.suffix=='.go' or f.name=='go.mod'}
env=os.environ.copy()
for k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
expected={'TestStatefulGraphAgainstIndependentModel','TestOwnerAndExhaustionFailuresAreAtomic','TestPublishedRefRetainsPagesAcrossGCAndGrowth','TestConcurrentCompletedReads','TestLayoutAndHandleBoundaries'}
report={'status':'running','sources':sources,'controllerSha256':sha(__file__),'runs':[]}
def save():(p/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 for mode,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
  cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1',*flags,'./...']
  with (p/(mode+'.stdout')).open('x') as out,(p/(mode+'.stderr')).open('x') as err:code=subprocess.run(cmd,cwd=p/'prototype',env=env,stdout=out,stderr=err).returncode
  events=[json.loads(line) for line in (p/(mode+'.stdout')).read_text().splitlines()]
  passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
  ok=code==0 and set(passed)==expected and not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
  report['runs'].append({'mode':mode,'command':cmd,'exitCode':code,'passed':passed,'ok':ok,'stdoutSha256':sha(p/(mode+'.stdout')),'stderrSha256':sha(p/(mode+'.stderr'))});save();assert ok
  assert sources=={f.name:sha(f) for f in (p/'prototype').iterdir() if f.suffix=='.go' or f.name=='go.mod'}
  print(mode,'passed',flush=True)
 report['status']='passed'
except BaseException as e:report['status']='failed';report['error']=repr(e);raise
finally:save()
