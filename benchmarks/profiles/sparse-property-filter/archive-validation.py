from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-sparse-property-filter');dst=r/'benchmarks/profiles/sparse-property-filter'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['conformance','native','units']:
 p=src/name/'validation.json';report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']=='d8073fc16d6ac9547354fb8c4858628f1a84a97a8118e23264e4947c9f627d19'
 for run in report['runs']:
  if name=='conformance':
   assert sha(Path(run['stdout']))==run['stdout_sha256'];assert sha(Path(run['stderr']))==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 shutil.copyfile(p,r/f'benchmarks/validation/sparse-property-filter-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file())
wide=json.loads((src/'wide-v3/validation.json').read_text())
assert wide['passed'] and len(wide['runs'])==48 and wide['sourceSha256']=='d8073fc16d6ac9547354fb8c4858628f1a84a97a8118e23264e4947c9f627d19'
for run in wide['runs']:
 assert sha(src/'wide-v3'/(run['id']+'.ts'))==run['fileSha256']
 for role,result in run['results'].items():assert sha(src/'wide-v3'/(run['id']+'.'+role+'.stdout'))==result['stdoutSha256']
shutil.copyfile(src/'wide-v3/validation.json',r/'benchmarks/validation/sparse-property-filter-wide.json')
for name in ['wide','wide-v2','wide-v3']:files.extend(p for p in (src/name).rglob('*') if p.is_file())
files.extend(src/name for name in ['build.stdout','build.stderr','build.json','source.json'])
archive=dst/'validation.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as f:
 for p in sorted(files):f.add(p,arcname=str(p.relative_to(src)))
(dst/'validation-archive.json').write_text(json.dumps({'archiveSha256':sha(archive),'files':{str(p.relative_to(src)):sha(p) for p in sorted(files)}},indent=2)+'\n')
print(json.dumps({'archiveBytes':archive.stat().st_size,'files':len(files)}))
