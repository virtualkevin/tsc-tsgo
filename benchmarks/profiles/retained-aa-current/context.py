from pathlib import Path
import hashlib,json,statistics
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports=[];reference={}
for experiment in ['compact-literal-pair','spread-override-table','coallocated-instantiated-symbol']:
 for size in ['small','large']:
  path=root/'benchmarks/results'/(experiment+'-screen')/(size+'.json');d=json.loads(path.read_text());assert d['status']=='passed';assert d['binaries']['baseline']['sha256']=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
  for p in d['projects']:
   identity={k:p[k] for k in ['commit','compilerArgs','configSha256','lockfileSha256']};identity['compilerArgs']=identity['compilerArgs']['baseline'];identity['inputs']=p['preflight']['baseline']['inputs']
   if p['name'] in reference:assert identity==reference[p['name']]
   else:reference[p['name']]=identity
   times=[x['baseline'] for x in p['pairs']];assert statistics.median(times)==p['baseline']['medianMs']
   cg=d['environment']['cgroupV2']
   reports.append({'experiment':experiment,'workload':p['name'],'report':str(path.relative_to(root)),'reportSha256':sha(path),'baselineMedianMs':statistics.median(times),'baselineRangeMs':[min(times),max(times)],'inputIdentitySha256':hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest(),'baselineBinarySha256':d['binaries']['baseline']['sha256'],'visibleCpuQuotaCpus':cg.get('minimumVisibleCpuQuotaCpus'),'cpuQuotaReadComplete':cg.get('cpuQuotaReadComplete'),'node':d['environment']['node']})
result={'scope':'Offline comparison of unchanged retained binary on identical input manifests/configs/arguments across three earlier screens. Different candidates, dates, cache state and external conditions coexist; this is neither A/A pairing nor causal attribution. No observations are removed or corrected.','observations':reports}
(out/'baseline-context.json').write_text(json.dumps(result,indent=2)+'\n')
print('Verified12 retained summaries with matching input identities; no causal or speedup claim')
