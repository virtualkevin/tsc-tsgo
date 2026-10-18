from pathlib import Path
import hashlib,json,tarfile,shutil
root=Path(__file__).resolve().parents[3]
src=Path('/tmp/tsc-merged-lookup-census');dst=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
units=json.loads((src/'units/validation.json').read_text())
cap=json.loads((src/'capture/report.json').read_text())
assert units['passed'] and cap['status']=='passed'
assert units['sourceSha256']==cap['source']['sha256']=='f757f9c9576fac6ff9c91391ba38be874a939260b832538fec98be48097ea868'
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
shutil.copyfile(src/'units/validation.json',root/'benchmarks/validation/merged-lookup-census-units.json')
summary=[]
for r in cap['runs']:
 if r['mode']!='enabled':continue
 owners=r['counts']['Owners'];counts={k:sum(s[k] for s in owners) for k in ['Lookups','Replacements','Unchanged','Writes']}
 assert counts['Lookups']==counts['Replacements']+counts['Unchanged']
 summary.append(dict(project=r['project'],owners=len(owners),counts=counts,unchangedFraction=counts['Unchanged']/counts['Lookups'] if counts['Lookups'] else None,peakKeysPerOwner=[s['PeakKeys'] for s in owners],emptyMapLookups=sum(s['LookupSizeBuckets'][0] for s in owners),elapsedControlsMs={q['mode']:q['elapsedMs'] for q in cap['runs'] if q['project']==r['project']}))
(dst/'summary.json').write_text(json.dumps(dict(scope=cap['scope'],projects=summary),indent=2)+'\n')
print(json.dumps(summary,indent=2))
