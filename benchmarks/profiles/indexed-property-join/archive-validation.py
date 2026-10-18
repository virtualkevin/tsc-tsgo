from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-indexed-property-join');dst=r/'benchmarks/profiles/indexed-property-join'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['conformance','native','units']:
 p=src/name/'validation.json';report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']=='f12abc882e649303aecb6b4aac516f04f66ac1c041f25d877fb6484cdbd0ce44'
 for run in report['runs']:
  if name=='conformance':
   assert sha(Path(run['stdout']))==run['stdout_sha256'];assert sha(Path(run['stderr']))==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 shutil.copyfile(p,r/f'benchmarks/validation/indexed-property-join-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file())
wide=json.loads((src/'wide/validation.json').read_text())
assert wide['passed'] and len(wide['runs'])==96 and wide['sourceSha256']=='f12abc882e649303aecb6b4aac516f04f66ac1c041f25d877fb6484cdbd0ce44'
for run in wide['runs']:
 assert sha(src/'wide'/(run['id']+'.ts'))==run['fileSha256']
 for role,result in run['results'].items():assert sha(src/'wide'/(run['id']+'.'+role+'.stdout'))==result['stdoutSha256']
shutil.copyfile(src/'wide/validation.json',r/'benchmarks/validation/indexed-property-join-wide.json')
for name in ['wide']:files.extend(p for p in (src/name).rglob('*') if p.is_file())
files.extend(src/name for name in ['build.stdout','build.stderr','build.json','source.json'])
archive=dst/'validation.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as f:
 for p in sorted(files):f.add(p,arcname=str(p.relative_to(src)))
(dst/'validation-archive.json').write_text(json.dumps({'archiveSha256':sha(archive),'files':{str(p.relative_to(src)):sha(p) for p in sorted(files)}},indent=2)+'\n')
print(json.dumps({'archiveBytes':archive.stat().st_size,'files':len(files)}))
