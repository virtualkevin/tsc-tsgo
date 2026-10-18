from pathlib import Path
import os,subprocess,json,hashlib
root=Path(__file__).resolve().parents[3];here=Path(__file__).resolve().parent
out=Path('/tmp/tsc-runtime-small-string/validation');out.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs=json.loads((here/'inputs.json').read_text());runtime=Path(inputs['runtimeSource']);overlay=here/'overlay.json'
assert sha(runtime)==inputs['beforeSha256'];assert sha(here/'runtime_faststr.go.txt')==inputs['afterSha256']
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
go='/tmp/tsc-toolchains/go/bin/go';report={'passed':False,'inputs':inputs,'overlaySha256':sha(overlay),'runs':[]}
try:
 for name,cwd,args in [('focused-baseline',here,['.']),('focused-overlay',here,['-overlay='+str(overlay),'.']),('maps',here,['-overlay='+str(overlay),'internal/runtime/maps']),('runtime-map',here,['-overlay='+str(overlay),'runtime','-run','Map'])]:
  cmd=[go,'test','-json',*args,'-count=1','-timeout','20m']
  with (out/(name+'.jsonl')).open('w') as a,(out/(name+'.stderr')).open('w') as b:
   code=subprocess.run(cmd,cwd=cwd,env=env,stdout=a,stderr=b,timeout=1500).returncode
  ev=[json.loads(x) for x in (out/(name+'.jsonl')).read_text().splitlines()];term=[e for e in ev if e['Action'] in ['pass','skip','fail']];tests=[e for e in term if e.get('Test')]
  ok=code==0 and len(tests)>0 and all(e['Action']!='fail' for e in term)
  if name.startswith('focused'):ok=ok and len(tests)==102 and all(e['Action']=='pass' for e in term)
  report['runs'].append(dict(name=name,command=cmd,exitCode=code,tests=len(tests),skips=[e.get('Test') for e in term if e['Action']=='skip'],passed=ok,stdoutSha256=sha(out/(name+'.jsonl')),stderrSha256=sha(out/(name+'.stderr'))))
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(name,ok,flush=True);assert ok
  assert sha(runtime)==inputs['beforeSha256'];assert sha(here/'runtime_faststr.go.txt')==inputs['afterSha256'];assert sha(overlay)==report['overlaySha256']
 report['passed']=True
except BaseException as e:report['error']=repr(e)
finally:(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
