from pathlib import Path
import subprocess,os,json,hashlib
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
overlay=out/'overlay.json';sources=json.loads(overlay.read_text())['Replace'];before={k:sha(v) for k,v in sources.items()}
report={'passed':False,'overlaySources':before,'controllerSha256':sha(__file__),'runs':[]}
try:
 for mode,flags in [('normal',[]),('race',['-race'])]:
  command=['/tmp/tsc-toolchains/go/bin/go','test',*flags,'-overlay',str(overlay),'./internal/checker','-run','^TestMaterializationCensus','-count=1','-timeout','10m','-json']
  stdout=out/(mode+'.jsonl');stderr=out/(mode+'.stderr')
  with stdout.open('w') as o,stderr.open('w') as e:code=subprocess.run(command,cwd=root/'packages/tsc-go',env=env,stdout=o,stderr=e,timeout=900).returncode
  events=[json.loads(l) for l in stdout.read_text().splitlines()];terminal=[v for v in events if v['Action'] in ['pass','fail','skip']];tests=[v for v in terminal if v.get('Test')]
  ok=code==0 and len(tests)==3 and all(v['Action']=='pass' for v in terminal)
  report['runs'].append({'mode':mode,'command':command,'exitCode':code,'tests':[(v['Test'],v['Action']) for v in tests],'stdoutSha256':sha(stdout),'stderrSha256':sha(stderr),'passed':ok});print(mode,ok,flush=True);assert ok
  assert {k:sha(v) for k,v in sources.items()}==before
 report['passed']=True
finally:(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
