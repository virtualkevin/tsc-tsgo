from pathlib import Path
import hashlib,json,tarfile,shutil
root=Path(__file__).resolve().parents[3]
src=Path('/tmp/tsc-type-liveness-census');dst=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
units=json.loads((src/'units/validation.json').read_text())
cap=json.loads((src/'capture/report.json').read_text())
assert units['passed'] and cap['status']=='passed'
assert units['sourceSha256']==cap['source']['sha256']=='390c3a036035aaf1d8a1e8d7f60bdf6376df172f1ed6905b2413e1235caecf90'
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
shutil.copyfile(src/'units/validation.json',root/'benchmarks/validation/type-liveness-census-units.json')
summary=[]
for r in cap['runs']:
 if r['mode']!='enabled':continue
 owners=r['counts']['Owners']
 keys=['Created','Eligible','Sampled','Overflow','Available','Cleared','IdentityMismatches']
 totals={k:sum(o[k] for o in owners) for k in keys}
 assert totals['IdentityMismatches']==0
 assert totals['Eligible']==totals['Sampled']+totals['Overflow']
 assert totals['Sampled']==totals['Available']+totals['Cleared']
 kinds={}
 for o in owners:
  for k in o['Kinds']:
   g=kinds.setdefault(k['CreationFlags'],{key:0 for key in ['Sampled','Available','Cleared']})
   for key in g:g[key]+=k[key]
 summary.append(dict(project=r['project'],owners=len(owners),totals=totals,observedClearedSampleFraction=totals['Cleared']/totals['Sampled'] if totals['Sampled'] else None,kinds=[dict(creationFlags=k,**v) for k,v in sorted(kinds.items())]))
with tarfile.open(archive) as t:
 for p in files:assert hashlib.sha256(t.extractfile(str(p.relative_to(src))).read()).hexdigest()==sha(p)
(dst/'summary.json').write_text(json.dumps(dict(scope='Deterministic bounded weak-reference construction sample after forced GC with program/checkers kept alive; cleared samples demonstrate reclamation, available samples do not prove necessity. Not unbiased population estimates, retained bytes, timing, or speedup evidence.',projects=summary),indent=2)+'\n')
for r in summary:print(r['project'],r['totals'],r['observedClearedSampleFraction'])
