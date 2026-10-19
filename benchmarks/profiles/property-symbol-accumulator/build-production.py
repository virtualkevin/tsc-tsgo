"""Temporarily apply the validated overlay, build normal provenance, then restore."""
import json,os,shutil,signal,subprocess,sys
sys.dont_write_bytecode=True
from final_common import *
verify()
readback=json.loads((PROFILE/'readback.json').read_text())
assert readback['passed']
# Re-run the independent raw-evidence check before any mutation.
subprocess.run([sys.executable,str(PROFILE/'verify.py')],cwd=ROOT,env=ENV,check=True)
assert not (PROFILE/'production-build.json').exists()
dist=MODULE/'dist';out=OUT/'production';out.mkdir(exist_ok=False)
retained={'tsc-go':'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f','tsc-go.provenance.json':'76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2'}
for name,digest in retained.items():
 assert sha(dist/name)==digest
 shutil.copy2(dist/name,out/name);assert sha(out/name)==digest
before=json.loads((dist/'tsc-go.provenance.json').read_text())
paths=json.loads(OVERLAY.read_text())['Replace'];backups={}
for dest,source in paths.items():
 path=Path(dest);rel=path.relative_to(MODULE)
 assert str(rel) in ('internal/checker/checker.go','internal/checker/property_accumulator_test.go')
 assert sha(source)==FREEZE['sources'][dest]
 if path.exists():
  backup=out/'source'/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,backup)
  backups[dest]={'file':str(backup),'sha256':sha(path),'mode':path.stat().st_mode&0o777}
 else:backups[dest]=None
assert len(backups)==2
(PROFILE/'baseline-source-backup.json').write_text(json.dumps(backups,indent=2)+'\n')
for suffix in ('','.provenance.json'):assert not (dist/('tsc-go-property-symbol-accumulator'+suffix)).exists()
report={'passed':False,'controllerSha256':sha(__file__),'freezeSha256':sha(PROFILE/'cli-freeze.json')}
def interrupt(sig,frame):raise KeyboardInterrupt(str(sig))
for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,interrupt)
try:
 for dest,source in paths.items():Path(dest).write_bytes(Path(source).read_bytes())
 env=ENV|{'GO':GO}
 with (out/'build.stdout').open('x') as a,(out/'build.stderr').open('x') as b:
  child=subprocess.Popen(['npm','run','build'],cwd=ROOT,env=env,stdout=a,stderr=b,start_new_session=True)
  try:code=child.wait(timeout=2400)
  finally:
   try:os.killpg(child.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   child.wait()
 report['exitCode']=code;assert code==0
 after=json.loads((dist/'tsc-go.provenance.json').read_text())
 assert before['build']==after['build']
 old={f['path']:f for f in before['source']['files']};new={f['path']:f for f in after['source']['files']}
 delta={k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
 expected={'packages/tsc-go/'+str(Path(k).relative_to(MODULE)):v for k,v in FREEZE['sources'].items()}
 assert delta==set(expected)
 for name,digest in expected.items():assert new[name]['sha256']==digest
 assert sha(dist/'tsc-go')==json.loads((PROFILE/'build.json').read_text())['binarySha256']
 for suffix in ('','.provenance.json'):shutil.copy2(dist/('tsc-go'+suffix),dist/('tsc-go-property-symbol-accumulator'+suffix))
 (PROFILE/'production-source.json').write_text(json.dumps(after['source'],indent=2)+'\n')
 report.update(passed=True,binarySha256=sha(dist/'tsc-go-property-symbol-accumulator'),sidecarSha256=sha(dist/'tsc-go-property-symbol-accumulator.provenance.json'),sourceSha256=after['source']['sha256'],sourceCounts={'baseline':len(old),'candidate':len(new)})
except BaseException as error:report['error']=repr(error)
finally:
 # Refuse to overwrite an unexpected concurrent source edit.
 for dest,backup in backups.items():
  path=Path(dest)
  allowed={FREEZE['sources'][dest]}
  if backup is not None:allowed.add(backup['sha256'])
  if path.exists():assert sha(path) in allowed,dest
  else:assert backup is None,dest
 for dest,backup in backups.items():
  if backup is None:Path(dest).unlink(missing_ok=True)
  else:
   assert sha(backup['file'])==backup['sha256']
   Path(dest).write_bytes(Path(backup['file']).read_bytes());os.chmod(dest,backup['mode'])
 for name,digest in retained.items():
  assert sha(out/name)==digest
  shutil.copy2(out/name,dist/name);assert sha(dist/name)==digest
 verify()
 report['retainedSourceAndDefaultRestored']=True
 for stream in ('stdout','stderr'):
  f=out/('build.'+stream)
  if f.exists():
   shutil.copy2(f,PROFILE/('production-build.'+stream));report[stream+'Sha256']=sha(f)
 (PROFILE/'production-build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
