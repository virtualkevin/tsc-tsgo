from pathlib import Path
import hashlib,json,math,shutil,statistics
root=Path(__file__).resolve().parents[3];r=root/'benchmarks/results/native-project-inlining'
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=load(r/'summary.json');p=load(r/'recording/proposal.json')
assert s['status']==p['status']=='passed';assert sha(r/'summary.json')==p['summarySha256']
e=r/'execution';e.mkdir()
files={root/k:v for k,v in s['snapshot']['files'].items()};files.update({Path(k):v for k,v in s['controllerFiles'].items()})
files[Path(__file__).parent/'record-native.mjs']=p['recorderSha256']
manifest=[]
for src,h in files.items():
 assert sha(src)==h;rel=src.relative_to(root);dst=e/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(dst)==h;manifest.append({'path':str(rel),'sha256':h})
src=Path('/tmp/tsc-native-project-inlining-supervisor.jsonl');events=[json.loads(x) for x in src.read_text().splitlines()];assert events[-1]['event']=='exited' and events[-1]['returnCode']==0
shutil.copyfile(src,e/'supervisor.jsonl');assert sha(src)==sha(e/'supervisor.jsonl');manifest.append({'path':'supervisor.jsonl','sha256':sha(src)})
results=[]
for run in s['runs']:
 assert run['status']=='passed' and sha(run['output'])==run['reportSha256']
 report=load(run['output']);assert report['status']=='passed'
 for project in report['projects']:
  n=9 if project['name'] in ['typeorm','trpc'] else 5
  assert len(project['pairs'])==n and project['diagnosticCount']==0
  assert project['preflight']['baseline']['inputs']==project['preflight']['candidate']['inputs']
  for i,pair in enumerate(project['pairs']):
   assert pair['order']==(['candidate','baseline'] if i%2 else ['baseline','candidate'])
   for side in ['baseline','candidate']:assert pair['resources'][side]['exitStatus']==0 and pair[side]>0
  med=lambda side:statistics.median([x[side] for x in project['pairs']])
  ratios=[x['baseline']/x['candidate'] for x in project['pairs']]
  row=next(x for x in p['results'] if x['name']==project['name'])
  checks={'baselineMedianMs':med('baseline'),'candidateMedianMs':med('candidate'),'baselineOverCandidate':med('baseline')/med('candidate'),'pairedMedian':statistics.median(ratios),'pairedMin':min(ratios),'pairedMax':max(ratios)}
  for side in ['baseline','candidate']:checks[side+'MedianRssMiB']=statistics.median([x['resources'][side]['peakRssKiB'] for x in project['pairs']])/1024
  for key,value in checks.items():assert math.isclose(value,row[key],rel_tol=1e-12)
  assert ratios==row['pairedRatios'];assert row['goFasterPairs']==sum(x>1 for x in ratios)
  results.append({'name':project['name'],**checks})
assert len(results)==4 and not p['allMeasuredWorkloadsAtLeast10InBothSummaries']
rows=(r/'recording/PERF.rows.md').read_text();assert len(rows.splitlines())==4
perf=root/'PERF.md';text=perf.read_text();assert rows not in text;perf.write_text(text+rows)
(e/'manifest.json').write_text(json.dumps({'files':manifest,'allCopiesReadBackVerified':True},indent=2)+'\n')
(r/'independent-readback.json').write_text(json.dumps({'passed':True,'pairs':28,'results':results,'scope':'Independent medians, pair ratios, RSS, raw order and recorded hashes; full input/diagnostic/provenance checks performed by frozen controller and recorder.'},indent=2)+'\n')
print('Archived',len(manifest),'execution files; independently recomputed 28 pairs; appended four PERF rows')
