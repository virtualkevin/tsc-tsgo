from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-reduction-small-pair');dst=r/'benchmarks/profiles/reduction-small-pair'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['conformance','native','units']:
 p=src/name/'validation.json';report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']=='c120f3fc891cad13d5ef4407195255d56307a299322c42ed242e59ccc3c4a199'
 for run in report['runs']:
  if name=='conformance':
   assert sha(Path(run['stdout']))==run['stdout_sha256'];assert sha(Path(run['stderr']))==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 shutil.copyfile(p,r/f'benchmarks/validation/reduction-small-pair-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file())
files.extend(src/name for name in ['focused.jsonl','focused.stderr','build.log','build.json','source.json','codegen.txt','baseline-codegen.txt'])
archive=dst/'validation.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as f:
 for p in sorted(files):f.add(p,arcname=str(p.relative_to(src)))
(dst/'validation-archive.json').write_text(json.dumps({'archiveSha256':sha(archive),'files':{str(p.relative_to(src)):sha(p) for p in sorted(files)}},indent=2)+'\n')
print(json.dumps({'archiveBytes':archive.stat().st_size,'files':len(files)}))
