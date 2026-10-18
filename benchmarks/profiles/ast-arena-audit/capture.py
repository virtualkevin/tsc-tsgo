from pathlib import Path
import hashlib,json,subprocess,tarfile
root=Path(__file__).resolve().parents[3];here=Path(__file__).resolve().parent
prior=root/'benchmarks/profiles/node-pointer-normal';manifest=json.loads((prior/'manifest.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((prior/'profiles.tar.gz').read_bytes())==manifest['archiveSha256']
out=Path('/tmp/tsc-ast-arena-audit');out.mkdir(exist_ok=True)
go='/tmp/tsc-toolchains/go/bin/go';binary=root/'packages/tsc-go/dist/tsc-go-node-pointer'
assert sha(binary.read_bytes())=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
records=[]
with tarfile.open(prior/'profiles.tar.gz') as archive:
 for name,digest in manifest['files'].items():
  if not name.endswith('-memprofile.pb.gz'):continue
  data=archive.extractfile("node-pointer-normal/"+name).read();assert sha(data)==digest
  project=name.split('/')[0];profile=out/(project+'.pb.gz');profile.write_bytes(data)
  command=[go,'tool','pprof','-raw',str(binary),str(profile)]
  p=subprocess.run(command,capture_output=True,check=True);assert not p.stderr
  raw=out/(project+'.raw.txt');raw.write_bytes(p.stdout)
  records.append(dict(project=project,profileSha256=digest,rawSha256=sha(p.stdout),command=command,toolSha256=sha(Path(go).read_bytes()),binarySha256=sha(binary.read_bytes())))
with tarfile.open(here/'raw-heaps.tar.gz','w:gz') as archive:
 for record in records:archive.add(out/(record['project']+'.raw.txt'),arcname=record['project']+'.raw.txt')
(here/'inputs.json').write_text(json.dumps(records,indent=2)+'\n')
print('Decoded',len(records),'hash-verified preserved heap profiles')
