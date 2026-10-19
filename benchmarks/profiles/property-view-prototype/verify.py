from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'validation.json').read_text());assert v['status']=='passed'
assert v['sources']=={k:sha(f) for k,f in json.loads((p/'overlay.json').read_text())['Replace'].items()}
expected={'TestPropertyViewMetadataAndIdentity','TestPropertyViewFrozenDecisionAndRetirement','TestPropertyViewFallbackBeforeEffects','TestPropertyViewIndependentHistories'}
assert [x['name'] for x in v['results']]==['normal','race','checkptr']
logs={}
for run in v['results']:
 events=[json.loads(line) for line in (p/(run['name']+'.stdout')).read_text().splitlines()]
 assert run['exitCode']==0 and set(run['passed'])==expected
 assert {x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x}==expected
 assert not any(x.get('Action') in ('fail','skip') for x in events)
 for suffix in ['stdout','stderr']:logs[run['name']+'.'+suffix]=sha(p/(run['name']+'.'+suffix))
print(json.dumps({'status':'passed','testsPerMode':4,'sources':v['sources'],'logs':logs,'scope':'Isolated component tests only; no production consumer, pinned-oracle API replay, formal proof or performance claim.'},indent=2))
