from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
checks=[]
for folder in [p/'initial',p]:
 d=json.loads((folder/'validation.json').read_text());assert d['passed']
 assert d['sources']=={f.name:sha(f) for f in (folder/'prototype').iterdir() if f.is_file()}
 for r in d['runs']:
  assert r['exitCode']==0 and r['passed']
  for stream in ['stdout','stderr']:assert sha(folder/(r['mode']+'.'+stream))==r[stream+'Sha256']
  events=[json.loads(x) for x in (folder/(r['mode']+'.stdout')).read_text().splitlines()]
  assert not any(x.get('Action') in ['fail','skip','build-fail'] for x in events)
  assert [x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x]==r['tests']
 checks.append({'folder':folder.name,'testsPerMode':len(d['runs'][0]['tests']),'modes':len(d['runs'])})
proof=json.loads((p/'proof.json').read_text());assert proof['sourceSha256']==sha(p/'prototype/slice.go')
assert len(proof['claims'])==5 and set(proof['claims'].values())=={'unsat'} and proof['negativeControl']=='sat'
events=[json.loads(x) for x in (p/'initial/allocation-regression.stdout').read_text().splitlines()]
assert any(x.get('Action')=='fail' and x.get('Test')=='TestOrdinaryHeaderDoesNotAllocate' for x in events)
result={'passed':True,'checks':checks,'proofSourceMatches':True,'initialAllocationRegressionPreserved':True,'files':{str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file() and f.name!='readback.json'}}
(p/'readback.json').write_text(json.dumps(result,indent=2)+'\n');print('Initial and final raw evidence, source pins, proof outcomes and regression verified')
