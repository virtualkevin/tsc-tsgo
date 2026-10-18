from pathlib import Path
import json,hashlib,tarfile,sys
from analyze import analyze
here=Path(__file__).resolve().parent
prior=here.parent/'normal-map-attribution'
inputs=json.loads((prior/'inputs.json').read_text())
report={'scope':'Specialized faststr map path CPU samples; includes callees, excludes unknown generic string maps. Not pure hashing cost, counts, live memory, wall time, removable budget or speedup forecast.','projects':[]}
with tarfile.open(prior/'raw-profiles.tar.gz') as archive:
 for item in inputs:
  data=archive.extractfile(item['project']+'.raw.txt').read()
  assert hashlib.sha256(data).hexdigest()==item['rawSha256']
  result=analyze(data.decode());result.update(project=item['project'],rawSha256=item['rawSha256']);report['projects'].append(result)
text=json.dumps(report,indent=2)+'\n'
if '--write' in sys.argv:(here/'report.json').write_text(text)
else:assert (here/'report.json').read_text()==text
for r in report['projects']:
 print(r['project'],round(r['fastStringMapPathPercent'],3))
 for c in r['callers'][:5]:print(round(c['totalPercent'],3),c['name'])
