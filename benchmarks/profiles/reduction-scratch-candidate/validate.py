from pathlib import Path
import hashlib,json,os,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
frozen={str(f):sha(f) for f in (p/'staged').glob('*.go')}
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64','GORACE']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
report={'status':'running','sources':frozen,'controllerSha256':sha(__file__),'results':[]};out=p/'validation.json';assert not out.exists()
try:
 for name,flags in [('normal',['-gcflags=github.com/microsoft/typescript-go/...=-l=4']),('race',['-race','-gcflags=github.com/microsoft/typescript-go/...=-l=4']),('checkptr',['-gcflags=all=-d=checkptr=2','-gcflags=github.com/microsoft/typescript-go/...=-l=4 -d=checkptr=2'])]:
  cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(p/'overlay.json'),*flags,'./internal/checker','-run','^(TestScratch.*|TestLazy.*|TestValueSymbolLinks.*)$']
  stdout=p/(name+'.stdout');stderr=p/(name+'.stderr')
  with stdout.open('x') as a,stderr.open('x') as b:code=subprocess.run(cmd,cwd=r/'packages/tsc-go',env=env,stdout=a,stderr=b).returncode
  events=[json.loads(l) for l in stdout.read_text().splitlines()];passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
  required={'TestScratchReductionMatchesOriginalGrouping','TestScratchSharedSymbolDoesNotResolveType','TestScratchRecursiveOwnershipAndCleanup','TestScratchCleanupOnPanic','TestValueSymbolLinksRetainInstantiatedGraphAcrossGC','TestValueSymbolLinksReplacementKeepsPublishedPointers'}
  ok=code==0 and required.issubset(passed) and not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
  report['results'].append(dict(name=name,command=cmd,exitCode=code,passed=passed,ok=ok,stdoutSha256=sha(stdout),stderrSha256=sha(stderr)))
  out.write_text(json.dumps(report,indent=2)+'\n');assert ok;assert frozen=={f:sha(f) for f in frozen};print(name,'passed',len(passed),flush=True)
 report['status']='passed'
except BaseException as e:report['status']='failed';report['error']=repr(e);raise
finally:out.write_text(json.dumps(report,indent=2)+'\n')
