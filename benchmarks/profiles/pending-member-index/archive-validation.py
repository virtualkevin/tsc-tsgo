from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-pending-member-index');dst=r/'benchmarks/profiles/pending-member-index'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['conformance','native','units']:
 p=src/name/'validation.json';report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']=='eaffe7bc4ed0261af97850b27059d041e51856fb2858563cf35050d857b44ac6'
 for run in report['runs']:
  if name=='conformance':
   assert sha(Path(run['stdout']))==run['stdout_sha256'];assert sha(Path(run['stderr']))==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 shutil.copyfile(p,r/f'benchmarks/validation/pending-member-index-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file())
files.extend(src/name for name in ['build.stdout','build.stderr','build.json','source.json'])
archive=dst/'validation.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as f:
 for p in sorted(files):f.add(p,arcname=str(p.relative_to(src)))
(dst/'validation-archive.json').write_text(json.dumps({'archiveSha256':sha(archive),'files':{str(p.relative_to(src)):sha(p) for p in sorted(files)}},indent=2)+'\n')
print(json.dumps({'archiveBytes':archive.stat().st_size,'files':len(files)}))
