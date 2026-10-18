from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-sparse-property-helper');dst=r/'benchmarks/profiles/sparse-property-helper'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['conformance','native','units']:
 p=src/name/'validation.json';report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']=='e2b806c1578b85f998691163441813314bf3e84a295f17fe439115fba28dc0b2'
 for run in report['runs']:
  if name=='conformance':
   assert sha(Path(run['stdout']))==run['stdout_sha256'];assert sha(Path(run['stderr']))==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 shutil.copyfile(p,r/f'benchmarks/validation/sparse-property-helper-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file())
wide=json.loads((src/'wide/validation.json').read_text())
assert wide['passed'] and len(wide['runs'])==48 and wide['sourceSha256']=='e2b806c1578b85f998691163441813314bf3e84a295f17fe439115fba28dc0b2'
for run in wide['runs']:
 assert sha(src/'wide'/(run['id']+'.ts'))==run['fileSha256']
 for role,result in run['results'].items():assert sha(src/'wide'/(run['id']+'.'+role+'.stdout'))==result['stdoutSha256']
shutil.copyfile(src/'wide/validation.json',r/'benchmarks/validation/sparse-property-helper-wide.json')
for name in ['wide','build-no-space','units-no-space']:files.extend(p for p in (src/name).rglob('*') if p.is_file())
files.extend(src/name for name in ['build.stdout','build.stderr','build.json','source.json','cache-reclamation.json'])
archive=dst/'validation.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as f:
 for p in sorted(files):f.add(p,arcname=str(p.relative_to(src)))
(dst/'validation-archive.json').write_text(json.dumps({'archiveSha256':sha(archive),'files':{str(p.relative_to(src)):sha(p) for p in sorted(files)}},indent=2)+'\n')
print(json.dumps({'archiveBytes':archive.stat().st_size,'files':len(files)}))
