from pathlib import Path
import hashlib,json,os,subprocess
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources={f.name:sha(f) for f in (p/'prototype').iterdir() if f.is_file()}
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
report={'passed':False,'sources':sources,'runs':[],'scope':'Standalone storage prototype; no compiler integration, conformance or performance claim.'}
for name,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
 cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1',*flags,'./...']
 with (p/(name+'.stdout')).open('x') as a,(p/(name+'.stderr')).open('x') as b:code=subprocess.run(cmd,cwd=p/'prototype',env=env,stdout=a,stderr=b).returncode
 events=[json.loads(x) for x in (p/(name+'.stdout')).read_text().splitlines()]
 passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
 ok=code==0 and set(passed)=={'TestBoundaryHistory','TestRandomHistories','TestTileSharingAndIndependentStores'} and not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
 report['runs'].append({'mode':name,'command':cmd,'exitCode':code,'passed':ok,'tests':passed,'stdoutSha256':sha(p/(name+'.stdout')),'stderrSha256':sha(p/(name+'.stderr'))})
 (p/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 assert ok
 assert sources=={f.name:sha(f) for f in (p/'prototype').iterdir() if f.is_file()}
 print(name,'passed',flush=True)
report['passed']=True
(p/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
