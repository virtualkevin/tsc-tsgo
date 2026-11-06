"""Independent recomputation from frozen paired compiler observations."""
from pathlib import Path
import hashlib,json,math,statistics
root=Path(__file__).resolve().parents[3];r=root/'benchmarks/results/project-inlining-screen'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=load(r/'summary.json');p=load(r/'recording/proposal.json');ratios=[];paired=[];rssratios=[];n=0;names=[]
assert s['status']=='passed' and p['status']=='passed' and p['summarySha256']==sha(r/'summary.json')
for run in s['runs']:
 f=r/(run['name']+'.json');assert sha(f)==run['reportSha256'];report=load(f);assert report['status']=='passed'
 for x in report['projects']:
  names.append(x['name']);q=next(v for v in p['results'] if v['name']==x['name']);pairs=x['pairs'];assert len(pairs)==(9 if run['name']=='small' else 5)
  for i,z in enumerate(pairs):
   assert z['order']==(['baseline','candidate'] if i%2==0 else ['candidate','baseline'])
   assert all(math.isfinite(z[side]) and z[side]>0 and z['resources'][side]['exitStatus']==0 for side in ['baseline','candidate'])
  for side in ['baseline','candidate']:
   samples=[z[side] for z in pairs];assert samples==x[side]['samplesMs'];assert statistics.median(samples)==q[side+'MedianMs']
   rss=[z['resources'][side]['peakRssKiB'] for z in pairs];assert rss==x['resources'][side]['peakRssKiB']['samples'];assert statistics.median(rss)/1024==q[side+'MedianRssMiB']
  a=statistics.median([z['baseline'] for z in pairs])/statistics.median([z['candidate'] for z in pairs]);pr=[z['baseline']/z['candidate'] for z in pairs];b=statistics.median(pr)
  assert a==q['baselineOverCandidate'] and b==q['pairedMedian'] and pr==q['pairedRatios'];assert min(pr)==q['pairedMin'] and max(pr)==q['pairedMax'];assert sum(v>1 for v in pr)==q['candidateFasterPairs']
  rss=q['candidateMedianRssMiB']/q['baselineMedianRssMiB'];assert rss==q['rssCandidateOverBaseline'];ratios.append(a);paired.append(b);rssratios.append(rss);n+=len(pairs)
assert names==['typeorm','trpc','vscode','sentry'] and n==28
aggregates={}
for xs,key in [(ratios,'ratioOfMediansGeometricMean'),(paired,'pairedMedianGeometricMean')]:
 value=math.exp(sum(map(math.log,xs))/4);assert math.isclose(value,p['aggregates'][key],rel_tol=1e-14);aggregates[key]=value
gates={'bothAggregatesAtLeast101':all(v>=1.01 for v in aggregates.values()),'allWorkloadSummariesAtLeast098':all(v>=.98 for v in ratios+paired),'allWorkloadMedianRssAtMost105':all(v<=1.05 for v in rssratios)}
assert gates==p['gates'] and all(gates.values())==p['qualifiesForConfirmation']
for f in load(r/'execution/manifest.json')['files']:assert sha(r/'execution'/f['path'])==f['sha256']
rows=(r/'recording/PERF.rows.md').read_text();perf=(root/'PERF.md').read_text();assert rows in perf and len(rows.splitlines())==4;assert all(not line.strip() or line.startswith('|') for line in perf.splitlines())
(r/'independent-readback.json').write_text(json.dumps(dict(passed=True,pairs=n,proposalSha256=sha(r/'recording/proposal.json'),summarySha256=sha(r/'summary.json'),executionManifestSha256=sha(r/'execution/manifest.json'),perfRowsSha256=sha(r/'recording/PERF.rows.md'),verifierSha256=sha(Path(__file__)),gates=gates,qualifiesForConfirmation=all(gates.values()),scope='Independent recomputation of all pair orders/counts, timing and RSS medians, paired ranges and aggregates, gates, copied execution hashes, and appended rows. Recorder additionally validates inputs, provenance, and diagnostics.'),indent=2)+'\n')
print(json.dumps({'pairs':n,'aggregates':aggregates,'gates':gates},indent=2))
