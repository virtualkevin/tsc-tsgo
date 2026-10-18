from pathlib import Path
import hashlib,json,tarfile,shutil
root=Path(__file__).resolve().parents[3]
src=Path('/tmp/tsc-property-loop-census');dst=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
units=json.loads((src/'units/validation.json').read_text())
cap=json.loads((src/'capture/report.json').read_text())
assert units['passed'] and cap['status']=='passed'
assert units['sourceSha256']==cap['source']['sha256']=='a0effbb17f15d29b1ce76b3d699d02787301a6366a97c0ad0f8e423ec37bb704'
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
files += [src/name for name in ['build.stdout','build.stderr']]
archive=dst/'evidence.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as t:
 for p in sorted(files):t.add(p,arcname=str(p.relative_to(src)))
(dst/'evidence-manifest.json').write_text(json.dumps(dict(archiveSha256=sha(archive),files={str(p.relative_to(src)):sha(p) for p in sorted(files)}),indent=2)+'\n')
shutil.copyfile(src/'units/validation.json',root/'benchmarks/validation/property-loop-census-units.json')
summary=[]
for r in cap['runs']:
 if r['mode']!='enabled':continue
 owners=r['counts']['Owners'];classes=[]
 for i,name in enumerate(['non-object','unresolved-object','pending-members','callable-or-module','ordinary-materialized']):
  counts={k:sum(o['Classes'][i][k] for o in owners) for k in ['Loops','Visited','Lookups','Hits','Misses','OptionalMisses','IdenticalHits']}
  assert counts['Lookups']==counts['Hits']+counts['Misses']
  classes.append(dict(name=name,**counts))
 cells=[]
 for a in range(65):
  for b in range(65):
   lookups=sum(o['OrdinaryLookups'][a][b] for o in owners);misses=sum(o['OrdinaryMisses'][a][b] for o in owners)
   if lookups:cells.append(dict(sourceBucket=a,targetBucket=b,lookups=lookups,misses=misses))
 assert sum(c['lookups'] for c in cells)==classes[4]['Lookups']
 assert sum(c['misses'] for c in cells)==classes[4]['Misses']
 summary.append(dict(project=r['project'],owners=len(owners),classes=classes,ordinarySizeCells=cells,elapsedControlsMs={q['mode']:q['elapsedMs'] for q in cap['runs'] if q['project']==r['project']}))
(dst/'summary.json').write_text(json.dumps(dict(scope=cap['scope'],projects=summary),indent=2)+'\n')
for r in summary:
 print(r['project'])
 for c in r['classes']:print(c)
 print('largest ordinary miss cells',sorted(r['ordinarySizeCells'],key=lambda c:-c['misses'])[:8])
