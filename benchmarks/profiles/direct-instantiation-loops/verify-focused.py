from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
expected={'TestDirectInstantiationTypeHistories','TestDirectInstantiationIndexHistories','TestDirectInstantiationSymbolHistories','TestDirectInstantiationSignatureHistories'}
records=0
for prefix in ['', 'baseline-']:
 v=json.loads((p/(prefix+'validation.json')).read_text());overlay=json.loads((p/(prefix+'overlay.json')).read_text())['Replace']
 assert v['status']=='passed' and v['controllerSha256']==sha(p/'validate.py')
 assert v['sources']=={k:sha(f) for k,f in overlay.items()}
 assert [x['name'] for x in v['results']]==['normal','race','checkptr']
 for run in v['results']:
  assert run['exitCode']==0 and run['ok']
  for stream in ['stdout','stderr']:assert sha(p/(prefix+run['name']+'.'+stream))==run[stream+'Sha256']
  events=[json.loads(l) for l in (p/(prefix+run['name']+'.stdout')).read_text().splitlines()]
  tests=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
  assert len(tests)==4 and set(tests)==expected and tests==run['passed']
  assert not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
  flags=[] if run['name']=='normal' else ['-race'] if run['name']=='race' else ['-gcflags=all=-d=checkptr=2']
  assert run['command']==['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(p/(prefix+'overlay.json')),*flags,'./internal/checker','-run','^TestDirectInstantiation(Type|Symbol|Signature|Index)Histories$']
  records+=len(tests)
audit=subprocess.check_output(['python3','-B',str(p/'source-audit.py')]);assert audit==(p/'source-audit.json').read_bytes()
print(json.dumps({'passed':True,'records':records,'candidate':sha(p/'validation.json'),'retained':sha(p/'baseline-validation.json'),'sourceAudit':sha(p/'source-audit.json'),'verifier':sha(__file__),'scope':'Focused actual instantiation histories on candidate and retained, normal/race/checkptr; no full conformance or performance claim.'},indent=2))
