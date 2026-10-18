from pathlib import Path
import hashlib,json,os,shutil,subprocess
root=Path(__file__).resolve().parents[3]
out=Path('/tmp/tsc-resolved-member-census');out.mkdir(exist_ok=True)
pkg=root/'packages/tsc-go';dist=pkg/'dist'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(dist/'tsc-go')=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
for name in ['tsc-go','tsc-go.provenance.json']:
 shutil.copy2(dist/name,out/('baseline-'+name))
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64']:
  env.pop(k,None)
env.update(GO='/tmp/tsc-toolchains/go/bin/go',GOCACHE='/home/dev/.cache/go-build')
with (out/'build.stdout').open('w') as stdout,(out/'build.stderr').open('w') as stderr:
 code=subprocess.run(['npm','run','build'],cwd=root,env=env,stdout=stdout,stderr=stderr).returncode
assert code==0,code
for src,dst in [('tsc-go','tsc-go-resolved-member-census'),('tsc-go.provenance.json','tsc-go-resolved-member-census.provenance.json')]:
 shutil.copy2(dist/src,dist/dst)
report=dict(exitCode=code,binarySha256=sha(dist/'tsc-go-resolved-member-census'),sidecarSha256=sha(dist/'tsc-go-resolved-member-census.provenance.json'),stdoutSha256=sha(out/'build.stdout'),stderrSha256=sha(out/'build.stderr'))
(Path(__file__).parent/'build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
