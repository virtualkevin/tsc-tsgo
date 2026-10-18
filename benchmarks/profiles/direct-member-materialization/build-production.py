"""Build only the exact validated candidate after separately reviewed application.

Does not apply candidate source. Always restores the retained default executable
and provenance; candidate source restoration is a separate guarded operation.
"""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
root=Path(__file__).resolve().parents[3]
profile=Path(__file__).resolve().parent
module=root/'packages/tsc-go';dist=module/'dist'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((profile/'final-freeze.json').read_text())
for name in ['final-tests','final-cli']:
 report=json.loads((profile/(name+'.json')).read_text())
 assert report['passed'] and report['freezeSha256']==sha(profile/'final-freeze.json')
 assert report['commonSha256']==sha(profile/'final_common.py')
 controller='validate-final-tests.py' if name=='final-tests' else 'validate-final-cli.py'
 assert report['controllerSha256']==sha(profile/controller)
for rel,h in freeze['overlaySources'].items():assert sha(module/rel)==h
assert sha(profile/'candidate.patch')=='0a3be26a193d75acf0098b1b0507cec6374664fe61a81a331611398171bc6fe3'
retained={'tsc-go':'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f','tsc-go.provenance.json':'76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2'}
for n,h in retained.items():assert sha(dist/n)==h
for p in [profile/'production-build.json',profile/'production-source.json',dist/'tsc-go-direct-members',dist/'tsc-go-direct-members.provenance.json']:assert not p.exists()
out=Path('/tmp/tsc-direct-member-screen/production');out.mkdir(parents=True,exist_ok=False)
for n,h in retained.items():
 shutil.copy2(dist/n,out/n);assert sha(out/n)==h
before=json.loads((dist/'tsc-go.provenance.json').read_text())
env=os.environ.copy()
for k in list(env):
 if k.startswith(('TSC_','TS_GO_','SCRIPTC_')) or k in ['GOFLAGS','GOEXPERIMENT','GOGC','GOMEMLIMIT','GOMAXPROCS','GODEBUG','GOOS','GOARCH','GOAMD64','NODE_OPTIONS','LD_PRELOAD']:
  env.pop(k,None)
env.update(GO='/tmp/tsc-toolchains/go/bin/go',GOCACHE='/home/dev/.cache/go-build')
report={'passed':False,'controllerSha256':sha(Path(__file__)),'freezeSha256':sha(profile/'final-freeze.json')}
try:
 with (out/'build.stdout').open('w') as a,(out/'build.stderr').open('w') as b:
  code=subprocess.run(['npm','run','build'],cwd=root,env=env,stdout=a,stderr=b).returncode
 report['exitCode']=code
 assert code==0
 after=json.loads((dist/'tsc-go.provenance.json').read_text())
 assert before['build']==after['build']
 old={f['path']:f for f in before['source']['files']};new={f['path']:f for f in after['source']['files']}
 delta={k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
 assert delta=={'packages/tsc-go/'+k for k in freeze['overlaySources']}
 for rel,h in freeze['overlaySources'].items():assert new['packages/tsc-go/'+rel]['sha256']==h
 for suffix in ['', '.provenance.json']:
  shutil.copy2(dist/('tsc-go'+suffix),dist/('tsc-go-direct-members'+suffix))
 report.update(binarySha256=sha(dist/'tsc-go-direct-members'),sidecarSha256=sha(dist/'tsc-go-direct-members.provenance.json'),passed=True)
 (profile/'production-source.json').write_text(json.dumps(after['source'],indent=2)+'\n')
finally:
 for n,h in retained.items():
  assert sha(out/n)==h
  shutil.copy2(out/n,dist/n);assert sha(dist/n)==h
 report['retainedDefaultRestored']=True
 for stream in ['stdout','stderr']:
  path=out/('build.'+stream)
  if path.exists():report[stream+'Sha256']=sha(path)
 (profile/'production-build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
