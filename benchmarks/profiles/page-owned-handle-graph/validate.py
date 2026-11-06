from pathlib import Path
import hashlib,json,os,subprocess
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();files=list((p/'prototype').glob('*'));frozen={str(f):sha(f) for f in files};env=os.environ.copy()
for k in ['GOFLAGS','GOEXPERIMENT','GOGC','GODEBUG','GOMEMLIMIT','GOMAXPROCS','GOOS','GOARCH','GOAMD64','GORACE']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
r={'status':'running','sources':frozen,'controllerSha256':sha(Path(__file__)),'runs':[]};out=p/'validation.json';assert not out.exists()
try:
 for mode,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
  cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1',*flags,'./...'];stdout=p/(mode+'.stdout');stderr=p/(mode+'.stderr')
  with stdout.open('x') as a,stderr.open('x') as b:code=subprocess.run(cmd,cwd=p/'prototype',env=env,stdout=a,stderr=b).returncode
  e=[json.loads(l) for l in stdout.read_text().splitlines()];passed=[x['Test'] for x in e if x.get('Action')=='pass' and 'Test' in x];ok=code==0 and len(passed)==7 and not any(x.get('Action') in ['fail','skip','build-fail'] for x in e)
  r['runs'].append(dict(mode=mode,command=cmd,exitCode=code,passed=passed,ok=ok,stdoutSha256=sha(stdout),stderrSha256=sha(stderr)));out.write_text(json.dumps(r,indent=2)+'\n');assert ok;assert frozen=={str(f):sha(f) for f in files};print(mode,'passed',len(passed),flush=True)
 r['status']='passed'
except BaseException as e:r['status']='failed';r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
