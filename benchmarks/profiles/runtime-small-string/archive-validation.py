from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-runtime-small-string');dst=r/'benchmarks/profiles/runtime-small-string'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for name in ['conformance','native','units']:
 p=src/name/'validation.json';report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
 for run in report['runs']:
  if name=='conformance':
   assert sha(Path(run['stdout']))==run['stdout_sha256'];assert sha(Path(run['stderr']))==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 for p,h in report.get('overlayFiles',{}).items():assert sha(Path(p))==h
 shutil.copyfile(src/name/'validation.json',r/f'benchmarks/validation/runtime-small-string-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file())
report=json.loads((src/'validation/report.json').read_text());assert report['passed']
for run in report['runs']:
 for ext,key in [('jsonl','stdoutSha256'),('stderr','stderrSha256')]:assert sha(src/'validation'/(run['name']+'.'+ext))==run[key]
files.extend(p for p in (src/'validation').rglob('*') if p.is_file())
files.extend(src/name for name in ['build.stdout','build.stderr','build.json','source.json'])
archive=dst/'validation.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as f:
 for p in sorted(files):f.add(p,arcname=str(p.relative_to(src)))
(dst/'validation-archive.json').write_text(json.dumps({'archiveSha256':sha(archive),'files':{str(p.relative_to(src)):sha(p) for p in sorted(files)}},indent=2)+'\n')
print(json.dumps({'archiveBytes':archive.stat().st_size,'files':len(files)}))
