from pathlib import Path
import gzip,json
from artifacts import read_capture,digest
p=Path(__file__).resolve().parent
report=json.loads((p/'report-resumed.json').read_text());assert report['status']=='passed'
manifest=[]
for run in report['runs']:
 if run['mode']!='enabled':continue
 name=f"{run['checkers']}-census.json";path=p/run['project']/name
 raw=read_capture(path);expected=run['artifacts'][name]
 assert digest(raw)==expected['sha256'] and len(raw)==expected['bytes']
 target=Path(str(path)+'.gz')
 with target.open('xb') as stream:
  with gzip.GzipFile(filename='',mode='wb',fileobj=stream,mtime=0) as zipped:zipped.write(raw)
 compressed=target.read_bytes();assert gzip.decompress(compressed)==raw
 manifest.append({'path':str(target.relative_to(p)),'sha256':digest(compressed),'rawSha256':digest(raw),'rawBytes':len(raw),'bytes':len(compressed)})
(p/'archive-manifest.json').write_text(json.dumps({'files':manifest,'readBackVerified':True},indent=2)+'\n')
print('Archived and byte-verified',len(manifest),'census captures')
