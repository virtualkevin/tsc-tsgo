from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();reference=None;rows=[]
for prefix in ['baseline-','']:
 v=json.loads((p/(prefix+'validation.json')).read_text());assert v['status']=='passed' and v['controllerSha256']==sha(p/'validate.py')
 assert v['sources']=={k:sha(f) for k,f in json.loads((p/(prefix+'overlay.json')).read_text())['Replace'].items()}
 assert [r['name'] for r in v['results']]==['normal','race','checkptr']
 for r in v['results']:
  assert r['ok'] and r['exitCode']==0 and r['passed']==['TestSpreadOverrideTableHistories']
  for stream in ['stdout','stderr']:assert sha(p/(prefix+r['name']+'.'+stream))==r[stream+'Sha256']
  events=[json.loads(l) for l in (p/(prefix+r['name']+'.stdout')).read_text().splitlines()]
  assert not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
  assert [e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]==r['passed']
  observed=[json.loads(e['Output'].split('OBSERVED ',1)[1]) for e in events if 'OBSERVED ' in e.get('Output','')]
  assert observed==r['observations'] and len(observed)==14
  assert {(x['Name'],x['Strict']) for x in observed}=={(name,strict) for name in ['ordinary','required','optional','leading','multiple','computed','accessor'] for strict in [False,True]}
  if reference is None:reference=observed
  assert observed==reference,'Diagnostic/type/counter histories differ'
  rows.append({'side':prefix or 'candidate','mode':r['name'],'stdoutSha256':r['stdoutSha256']})
(p/'focused-readback.json').write_text(json.dumps({'passed':True,'runs':rows,'historiesPerRun':14,'verifierSha256':sha(__file__)},indent=2)+'\n')
print('All 84 retained/candidate histories agree across normal/race/checkptr')
