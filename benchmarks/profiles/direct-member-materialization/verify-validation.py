"""Read back completed validation artifacts without rerunning compiler tests."""
import sys,json,gzip
sys.dont_write_bytecode=True
from final_common import *
verify()
read=lambda name:json.loads((PROFILE/name).read_text())
focused=read('validation.json');tests=read('final-tests.json');cli=read('final-cli.json')
assert focused['passed'] and tests['passed'] and cli['passed']
assert focused['controllerSha256']==sha(PROFILE/'validate.py')
for report,name in [(tests,'validate-final-tests.py'),(cli,'validate-final-cli.py')]:
 assert report['controllerSha256']==sha(PROFILE/name)
 assert report['freezeSha256']==sha(PROFILE/'final-freeze.json')
 assert report['commonSha256']==sha(PROFILE/'final_common.py')
assert [r['mode'] for r in focused['runs']]==['normal','race']
for r in focused['runs']:
 assert r['passed'] and r['exitCode']==0
 raw=PROFILE/(r['mode']+'.jsonl');assert sha(raw)==r['stdoutSha256']
 assert sha(PROFILE/(r['mode']+'.stderr'))==r['stderrSha256']
 events=[json.loads(l) for l in raw.read_text().splitlines()]
 assert not any(e['Action'] in ['fail','skip'] for e in events)
 passed=[e for e in events if e['Action']=='pass' and e.get('Test')]
 assert len(passed)==21 and sum('/' not in e['Test'] for e in passed)==16
assert [r['name'] for r in tests['runs']]==['checkptr','root','services','conformance']
logs=0
for r in tests['runs']:
 assert r['passed'] and r['exit_code']==0
 for name,m in r['archive'].items():
  path=PROFILE/'final-test-logs'/name;assert sha(path)==m['sha256']
  raw=gzip.decompress(path.read_bytes());assert hashlib.sha256(raw).hexdigest()==m['rawSha256']
  stream='stdout' if name.endswith('.jsonl.gz') else 'stderr'
  assert m['rawSha256']==r[stream+'_sha256'] and raw==Path(r[stream]).read_bytes();logs+=1
 for name,records,top in [('checkptr',21,16),('root',21182,251),('services',219,60)]:
  if r['name']==name:assert r['summary']['tests']==records and len(r['summary']['topLevelTests'])==top
 if r['name']=='conformance':
  assert r['summary']['source_configuration_cases']=={'total':14915,'fully_checked':12789,'partially_checked':8,'unsupported_skipped':2118,'failed':0}
  assert not r['summary']['integrity_errors'] and not r['summary']['failed_tests']
assert [r['mode'] for r in cli['runs']]==['normal','integration','race','checkptr']
for r in cli['runs']:
 assert r['passed'] and r['exitCode']==0
 n=12 if r['mode']=='integration' else 80
 assert r['counts']=={'tests':n,'pass':n,'fail':0,'cancelled':0,'skipped':0,'todo':0}
 for key in ['log','buildLog']:
  if key not in r:continue
  m=r[key];path=PROFILE/'final-cli-logs'/m['file'];assert sha(path)==m['sha256']
  raw=gzip.decompress(path.read_bytes());assert hashlib.sha256(raw).hexdigest()==m['rawSha256']
  assert raw==(OUT/'cli'/m['file'].removesuffix('.gz')).read_bytes();logs+=1
verify()
report={'passed':True,'compressedLogsVerified':logs,'reports':{n:sha(PROFILE/n) for n in ['validation.json','final-tests.json','final-cli.json']},'freezeSha256':sha(PROFILE/'final-freeze.json'),'scope':'Completed focused normal/race, strict-checkptr, root/services/conformance and normal/race/checkptr CLI/API/emit validation readback. Not a performance result.'}
(PROFILE/'validation-readback.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
