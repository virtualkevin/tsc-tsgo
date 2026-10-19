from pathlib import Path
import subprocess,os,json,hashlib
p=Path(__file__).resolve().parent;r=p.parents[2];env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
sources=json.loads((p/'overlay.json').read_text())['Replace'];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();frozen={k:sha(v) for k,v in sources.items()};results=[]
for name,flags in [('normal',[]),('race',['-race']),('checkptr',['-gcflags=all=-d=checkptr=2'])]:
 cmd=['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(p/'overlay.json'),*flags,'./internal/checker','-run','^TestPropertyCacheOwnership']
 with (p/(name+'.stdout')).open('w') as a,(p/(name+'.stderr')).open('w') as b:code=subprocess.run(cmd,cwd=r/'packages/tsc-go',env=env,stdout=a,stderr=b).returncode
 records=[json.loads(x) for x in (p/(name+'.stdout')).read_text().splitlines()];passed=[x['Test'] for x in records if x.get('Action')=='pass' and 'Test' in x]
 assert code==0 and len(passed)==2 and not any(x.get('Action') in ['fail','skip'] for x in records)
 results.append({'name':name,'command':cmd,'exitCode':code,'passed':passed})
 assert frozen=={k:sha(v) for k,v in sources.items()}
(p/'validation.json').write_text(json.dumps({'status':'passed','sources':frozen,'results':results},indent=2)+'\n')
