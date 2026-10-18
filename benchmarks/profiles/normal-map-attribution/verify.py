from pathlib import Path
import hashlib,json,tarfile
from analyze import analyze
base=Path(__file__).resolve().parent
manifest=json.loads((base.parent/'node-pointer-normal/manifest.json').read_text())
inputs=json.loads((base/'inputs.json').read_text())
report=json.loads((base/'report.json').read_text())
with tarfile.open(base/'raw-profiles.tar.gz') as t:
 for entry,expected in zip(inputs,report['projects'],strict=True):
  project=entry['project'];assert project==expected['project']
  member=project+'/'+Path(entry['profile']).name
  assert manifest['files'][member]==entry['profileSha256']
  data=t.extractfile(project+'.raw.txt').read()
  assert hashlib.sha256(data).hexdigest()==entry['rawSha256']==expected['rawSha256']
  actual=analyze(data.decode());actual.update(project=project,rawSha256=entry['rawSha256'])
  assert actual==expected
print('All four archived raw profiles reproduce; original profile hashes match retained capture manifest')
