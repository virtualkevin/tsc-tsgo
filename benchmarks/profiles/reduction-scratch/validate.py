from pathlib import Path
import hashlib,json,os,subprocess
p=Path(__file__).resolve().parent;go='/tmp/tsc-toolchains/go/bin/go';env=os.environ.copy()
for k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG']:env.pop(k,None)
env['GOTOOLCHAIN']='local';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
sources={f.name:sha(f) for f in (p/'prototype').iterdir() if f.is_file()};report={'status':'running','sources':sources,'runs':[]}
try:
 for mode,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
  cmd=[go,'test','-json','-count=1',*flags,'./...'];r=subprocess.run(cmd,cwd=p/'prototype',env=env,capture_output=True)
  (p/(mode+'.stdout')).write_bytes(r.stdout);(p/(mode+'.stderr')).write_bytes(r.stderr)
  events=[json.loads(l) for l in r.stdout.splitlines()];passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
  assert r.returncode==0 and set(passed)=={'TestHistories','TestBoundsAndLifetime'} and not any(e.get('Action') in ['fail','skip'] for e in events)
  report['runs'].append({'mode':mode,'command':cmd,'passed':passed,'stdoutSha256':sha(p/(mode+'.stdout')),'stderrSha256':sha(p/(mode+'.stderr'))})
  print(mode,'passed',flush=True)
 assert sources=={f.name:sha(f) for f in (p/'prototype').iterdir() if f.is_file()}
 report['status']='passed'
finally:(p/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
