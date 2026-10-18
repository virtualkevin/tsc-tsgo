from pathlib import Path
import hashlib,json,tarfile,shutil
root=Path(__file__).resolve().parents[3]
src=Path('/tmp/tsc-resolved-member-census');dst=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
units=json.loads((src/'units/validation.json').read_text())
cap=json.loads((src/'capture/report.json').read_text())
assert units['passed'] and cap['status']=='passed'
assert units['sourceSha256']==cap['source']['sha256']=='6ec99f9289783f1dfa77d1d732f26a591ae0276327a62ad348ff70d10dc9eb34'
assert len(cap['runs'])==12
for r in units['runs']:
 assert sha(src/'units'/(r['name']+'.jsonl'))==r['stdoutSha256']
 assert sha(src/'units'/(r['name']+'.stderr'))==r['stderrSha256']
for r in cap['runs']:
 p=src/'capture'/r['project'];mode=r['mode']
 assert sha(p/(mode+'.stdout'))==r['stdoutSha256']
 assert sha(p/(mode+'.stderr'))==r['stderrSha256']
 if mode=='enabled':assert sha(p/'census.json')==r['censusSha256']
files=[p for folder in ['units','capture'] for p in (src/folder).rglob('*') if p.is_file()]
files += [src/name for name in ['focused.jsonl','build.stdout','build.stderr','source.json']]
archive=dst/'evidence.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as t:
 for p in sorted(files):t.add(p,arcname=str(p.relative_to(src)))
(dst/'evidence-manifest.json').write_text(json.dumps(dict(archiveSha256=sha(archive),files={str(p.relative_to(src)):sha(p) for p in sorted(files)}),indent=2)+'\n')
shutil.copyfile(src/'units/validation.json',root/'benchmarks/validation/resolved-member-census-units.json')
summary=[]
for r in cap['runs']:
 if r['mode']!='enabled':continue
 owners=r['counts']['Owners'];paths=[]
 for i,name in enumerate(['materialized-table','frozen-layout','pending-own','pending-with-bases']):
  counts={k:sum(s['Paths'][i][k] for s in owners) for k in ['Lookups','Hits','Misses']}
  assert counts['Lookups']==counts['Hits']+counts['Misses']
  for k in ['SizeBuckets','MissSizeBuckets','KeyByteBuckets']:
   counts[k]=[sum(s['Paths'][i][k][b] for s in owners) for b in range(65)]
  counts['MaxSize']=max(s['Paths'][i]['MaxSize'] for s in owners)
  counts['MaxKeyBytes']=max(s['Paths'][i]['MaxKeyBytes'] for s in owners)
  paths.append(dict(name=name,**counts))
 summary.append(dict(project=r['project'],owners=len(owners),paths=paths,elapsedControlsMs={q['mode']:q['elapsedMs'] for q in cap['runs'] if q['project']==r['project']}))
(dst/'summary.json').write_text(json.dumps(dict(scope=cap['scope'],projects=summary),indent=2)+'\n')
for r in summary:
 print(r['project'],r['owners'])
 for p in r['paths']:print(p['name'],p['Lookups'],p['Hits'],p['Misses'],p['MaxSize'])
