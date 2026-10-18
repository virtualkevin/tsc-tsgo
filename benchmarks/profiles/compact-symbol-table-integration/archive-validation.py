from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-compact-symbol-table');dst=r/'benchmarks/profiles/compact-symbol-table-integration'
expected='67bdc271aedf37c03f0746414a8b67e0072dfe9c79f9aee15af8bd14b9cb4155'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();files=[]
for name in ['conformance','native','units','instrumented']:
 p=src/name/'validation.json';report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']==expected
 for run in report['runs']:
  if name=='conformance':
   assert sha(run['stdout'])==run['stdout_sha256'];assert sha(run['stderr'])==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  elif name=='instrumented':
   assert sha(src/name/(run['mode']+'-parity.log'))==run['logSha256'];assert sha(src/name/(run['mode']+'-build.log'))==run['buildLogSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 shutil.copyfile(p,r/f'benchmarks/validation/compact-symbol-table-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file() and not p.name.startswith('tsc-go-'))
verified=json.loads((src/'services/verified.json').read_text());assert verified['passed'] and verified['sourceSha256']==expected
assert sha(src/'services/validation.json')==verified['originalControllerReportSha256']
assert sha(src/'services/services.jsonl')==verified['stdoutSha256']
assert sha(src/'services/services.stderr')==verified['stderrSha256']
shutil.copyfile(src/'services/verified.json',r/'benchmarks/validation/compact-symbol-table-services.json')
files.extend(p for p in (src/'services').rglob('*') if p.is_file())
files.extend(src/name for name in ['build.stdout','build.stderr','build.json'])
archive=dst/'validation.tar.gz';assert not archive.exists()
manifest={str(p.relative_to(src)):sha(p) for p in sorted(files)}
assert len(manifest)==len(files)
with tarfile.open(archive,'w:gz') as f:
 for p in sorted(files):f.add(p,arcname=str(p.relative_to(src)))
with tarfile.open(archive) as f:
 assert sorted(f.getnames())==sorted(manifest)
 for name,digest in manifest.items():assert hashlib.sha256(f.extractfile(name).read()).hexdigest()==digest
(dst/'validation-archive.json').write_text(json.dumps({'archiveSha256':sha(archive),'files':manifest},indent=2)+'\n')
print(json.dumps({'archiveBytes':archive.stat().st_size,'files':len(files)}))
