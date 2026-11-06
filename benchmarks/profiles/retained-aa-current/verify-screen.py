"""Independently recompute the fixed same-binary calibration summaries."""
from pathlib import Path
import hashlib,json,math,statistics
root=Path(__file__).resolve().parents[3];out=root/'benchmarks/results/retained-aa-current-screen'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=load(out/'summary.json');p=load(out/'recording/proposal.json');assert s['status']=='passed' and p['status']=='passed';assert p['kind']=='same-binary calibration, not a candidate speedup';assert sha(out/'summary.json')==p['summarySha256']
assert s['snapshot']['binaries']['baseline']==s['snapshot']['binaries']['candidate'];assert s['snapshot']['sourceDifference']==[]
count=0;names=[]
for run in s['runs']:
 f=out/(run['name']+'.json');assert sha(f)==run['reportSha256'];d=load(f);assert d['status']=='passed' and d['binaries']['baseline']==d['binaries']['candidate'];assert d['runs']==(9 if run['name']=='small' else 5) and d['warmups']==1
 for x in d['projects']:
  names.append(x['name']);q=next(y for y in p['results'] if y['name']==x['name']);pairs=x['pairs'];assert len(pairs)==d['runs'];ratios=[]
  for i,z in enumerate(pairs):
   assert z['order']==(['baseline','candidate'] if i%2==0 else ['candidate','baseline'])
   assert all(math.isfinite(z[a]) and z[a]>0 and z['resources'][a]['exitStatus']==0 for a in ['baseline','candidate']);ratios.append(z['baseline']/z['candidate'])
  for a in ['baseline','candidate']:
   times=[z[a] for z in pairs];rss=[z['resources'][a]['peakRssKiB'] for z in pairs];assert times==x[a]['samplesMs'] and statistics.median(times)==q[a+'MedianMs'];assert rss==x['resources'][a]['peakRssKiB']['samples'];assert statistics.median(rss)/1024==q[a+'MedianRssMiB']
  assert q['baselineOverCandidate']==q['baselineMedianMs']/q['candidateMedianMs'];assert ratios==q['pairedRatios'];assert q['pairedMedian']==statistics.median(ratios) and q['pairedMin']==min(ratios) and q['pairedMax']==max(ratios);assert q['pairOrders']==[z['order'] for z in pairs];assert q['secondLabelFasterPairs']==sum(v>1 for v in ratios)
  logs=list(map(math.log,ratios));m=statistics.median(logs);assert math.isclose(q['medianAbsoluteLogDeviation'],statistics.median([abs(x-m) for x in logs]),rel_tol=1e-13,abs_tol=1e-15)
  count+=len(pairs)
assert names==['typeorm','trpc','vscode','sentry'] and count==28
for f in load(out/'execution/manifest.json')['files']:assert sha(out/'execution'/f['path'])==f['sha256']
rows=(out/'recording/PERF.rows.md').read_text();assert len(rows.splitlines())==4 and rows in (root/'PERF.md').read_text()
(out/'independent-readback.json').write_text(json.dumps({'passed':True,'kind':'same-binary calibration only','pairs':count,'summarySha256':sha(out/'summary.json'),'proposalSha256':sha(out/'recording/proposal.json'),'executionManifestSha256':sha(out/'execution/manifest.json'),'perfRowsSha256':sha(out/'recording/PERF.rows.md'),'verifierSha256':sha(Path(__file__)),'scope':'Same binary identities, all pair counts/order, raw times/RSS and medians, paired ranges and log deviations, execution hashes and appended rows. Input/provenance/diagnostic integrity additionally checked by recorder.'},indent=2)+'\n')
print('Verified all28 A/A pairs; no candidate speedup or promotion inferred')
