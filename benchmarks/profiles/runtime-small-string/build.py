from pathlib import Path
import hashlib,json,os,shutil,subprocess
root=Path(__file__).resolve().parents[3]
out=Path('/tmp/tsc-runtime-small-string');out.mkdir(exist_ok=True)
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
overlay=Path(__file__).resolve().parent/'overlay.json'
inputs=json.loads((overlay.parent/'inputs.json').read_text())
assert sha(Path(inputs['runtimeSource']))==inputs['beforeSha256']
assert sha(overlay.parent/'runtime_faststr.go.txt')==inputs['afterSha256']
overlay_sha=sha(overlay)
env['GOFLAGS']='-overlay='+str(overlay)
with (out/'build.stdout').open('w') as stdout,(out/'build.stderr').open('w') as stderr:
 code=subprocess.run(['npm','run','build'],cwd=root,env=env,stdout=stdout,stderr=stderr).returncode
assert code==0,code
for src,dst in [('tsc-go','tsc-go-runtime-small-string'),('tsc-go.provenance.json','tsc-go-runtime-small-string.provenance.json')]:
 shutil.copy2(dist/src,dist/dst)
report=dict(exitCode=code,binarySha256=sha(dist/'tsc-go-runtime-small-string'),sidecarSha256=sha(dist/'tsc-go-runtime-small-string.provenance.json'),stdoutSha256=sha(out/'build.stdout'),stderrSha256=sha(out/'build.stderr'))
assert sha(Path(inputs['runtimeSource']))==inputs['beforeSha256']
assert sha(overlay.parent/'runtime_faststr.go.txt')==inputs['afterSha256']
assert sha(overlay)==overlay_sha
report.update(runtimeInputs=inputs,overlaySha256=overlay_sha,goFlags=env['GOFLAGS'])
(Path(__file__).parent/'build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report),flush=True)
