from pathlib import Path
import subprocess,os,json,hashlib
p=Path(__file__).resolve().parent;r=p.parents[2]
v=json.loads((p/'validation.json').read_text());assert v['status']=='passed'
sources=json.loads((p/'overlay.json').read_text())['Replace'];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();assert v['sources']=={k:sha(f) for k,f in sources.items()}
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
cmd=['/tmp/tsc-toolchains/go/bin/go','test','-count=5','-run','^$','-bench','^BenchmarkMapperPlanMerged$','-benchtime=200ms','-overlay',str(p/'overlay.json'),'./internal/checker']
with (p/'benchmark.stdout').open('w') as a,(p/'benchmark.stderr').open('w') as b:code=subprocess.run(cmd,cwd=r/'packages/tsc-go',env=env,stdout=a,stderr=b).returncode
assert v['sources']=={k:sha(f) for k,f in sources.items()}
(p/'benchmark.json').write_text(json.dumps({'exitCode':code,'command':cmd,'sources':v['sources'],'scope':'Fixed-order synthetic 32-link merged-chain evaluation only. Excludes compilation and retained plan memory. No compiler workload speedup claim.'},indent=2)+'\n');assert code==0
