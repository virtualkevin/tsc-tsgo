from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/dev/tssss/tsc-tsgo');src=Path('/tmp/tsc-parser-interner');dst=r/'benchmarks/profiles/parser-interner'
expected='1e5399a8058a1b41ef613763afec4801bfcfd703ad7ae6616458eb5d590ffba8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();files=[]
for name in ['conformance','native','units','instrumented','services']:
 p=src/name/('verified.json' if name=='units' else 'validation.json');report=json.loads(p.read_text());assert report['passed'];assert report['sourceSha256']==expected
 for run in report['runs']:
  if name=='conformance':
   assert sha(run['stdout'])==run['stdout_sha256'];assert sha(run['stderr'])==run['stderr_sha256']
  elif name=='native':assert sha(src/name/(run['name']+'.log'))==run['logSha256']
  elif name=='instrumented':
   assert sha(src/name/(run['mode']+'-parity.log'))==run['logSha256'];assert sha(src/name/(run['mode']+'-build.log'))==run['buildLogSha256']
  else:
   assert sha(src/name/(run['name']+'.jsonl'))==run['stdoutSha256'];assert sha(src/name/(run['name']+'.stderr'))==run['stderrSha256']
 shutil.copyfile(p,r/f'benchmarks/validation/parser-interner-{name}.json')
 files.extend(p for p in (src/name).rglob('*') if p.is_file() and not p.name.startswith('tsc-go-'))
verified=json.loads((src/'units/verified.json').read_text())
assert sha(src/'units/validation.json')==verified['originalReportSha256']
assert sha(src/'parser-repair/validation.json')==verified['repairReportSha256']
repair=verified['repairedParser']
for filename,key in [('parser.jsonl','stdoutSha256'),('parser.stderr','stderrSha256'),('fixtures.json','fixtureManifestSha256')]:assert sha(src/'parser-repair'/filename)==repair[key]
files.extend(p for p in (src/'parser-repair').rglob('*') if p.is_file())
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
