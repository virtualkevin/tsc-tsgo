from pathlib import Path
import hashlib,json,os,subprocess
p=Path(__file__).resolve().parent;m=p.parent/'typed-handle-graph/prototype';go='/tmp/tsc-toolchains/go/bin/go'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sourceFiles=[m/'go.mod',m/'graph.go',m/'graph_test.go',p/'staged/storage_experiment_test.go']
sources={str(f):sha(f) for f in sourceFiles};env=os.environ.copy()
for k in list(env):
 if k.startswith('GRAPH_PROBE_') or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GORACE','GOOS','GOARCH','GOAMD64']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
expected={'TestStatefulGraphAgainstIndependentModel','TestOwnerAndExhaustionFailuresAreAtomic','TestPublishedRefRetainsPagesAcrossGCAndGrowth','TestConcurrentCompletedReads','TestLayoutAndHandleBoundaries','TestStorageFixtureEquality','TestStoragePointerPageLifetime'}
pattern='^('+'|'.join(sorted(expected))+')$';overlay=p/'overlay.json'
report={'status':'running','sources':sources,'overlaySha256':sha(overlay),'controllerSha256':sha(__file__),'runs':[]}
def save():(p/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 for mode,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
  cmd=[go,'test','-json','-count=1','-overlay',str(overlay),*flags,'-run',pattern,'./...']
  with (p/(mode+'.stdout')).open('x') as a,(p/(mode+'.stderr')).open('x') as b:code=subprocess.run(cmd,cwd=m,env=env,stdout=a,stderr=b).returncode
  events=[json.loads(l) for l in (p/(mode+'.stdout')).read_text().splitlines()];passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
  ok=code==0 and set(passed)==expected and not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
  report['runs'].append({'mode':mode,'command':cmd,'exitCode':code,'ok':ok,'passed':passed,'stdoutSha256':sha(p/(mode+'.stdout')),'stderrSha256':sha(p/(mode+'.stderr'))});save();assert ok
  assert sources=={str(f):sha(f) for f in sourceFiles}
  print(mode,'passed',flush=True)
 binary=Path('/tmp/typed-handle-graph-measure.test');assert not binary.exists()
 cmd=[go,'test','-c','-trimpath','-overlay',str(overlay),'-o',str(binary),'.']
 with (p/'build.stdout').open('x') as a,(p/'build.stderr').open('x') as b:code=subprocess.run(cmd,cwd=m,env=env,stdout=a,stderr=b).returncode
 assert code==0 and sources=={str(f):sha(f) for f in sourceFiles}
 report['build']={'command':cmd,'exitCode':code,'binary':str(binary),'binarySha256':sha(binary),'toolchainSha256':sha(go),'version':subprocess.check_output([go,'version'],text=True).strip()}
 report['status']='passed'
except BaseException as e:report['status']='failed';report['error']=repr(e);raise
finally:save()
