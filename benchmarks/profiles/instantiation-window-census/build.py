from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
overlay=out/'overlay-with-lifetime.json';sources=json.loads(overlay.read_text())['Replace'];before={k:sha(v) for k,v in sources.items()}
binary=Path('/tmp/tsc-instantiation-window-census');assert not binary.exists()
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64']:env.pop(k,None)
env.update(GOCACHE='/home/dev/.cache/go-build',GOTOOLCHAIN='local')
go='/tmp/tsc-toolchains/go/bin/go';command=[go,'build','-trimpath','-overlay',str(overlay),'-o',str(binary),'./cmd/tsgo']
with (out/'build.stdout').open('w') as a,(out/'build.stderr').open('w') as b:code=subprocess.run(command,cwd=root/'packages/tsc-go',env=env,stdout=a,stderr=b).returncode
report={'exitCode':code,'command':command,'overlaySources':before,'controllerSha256':sha(__file__),'scope':'Diagnostic overlay build only; not a performance candidate or standard production provenance.'}
if code==0:
 assert before=={k:sha(v) for k,v in sources.items()}
 (out/'build-info.txt').write_bytes(subprocess.check_output([go,'version','-m',str(binary)],env=env))
 report.update(binarySha256=sha(binary),buildInfoSha256=sha(out/'build-info.txt'))
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');assert code==0
