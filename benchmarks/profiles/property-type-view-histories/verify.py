from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
report=json.loads((p/'validation.json').read_text())
assert report['status']=='passed'
assert report['sources']=={k:sha(v) for k,v in json.loads((p/'overlay.json').read_text())['Replace'].items()}
expected={'TestPropertyViewMetadataAndIdentity','TestPropertyViewFrozenDecisionAndRetirement','TestPropertyViewFallbackBeforeEffects','TestPropertyViewIndependentHistories','TestPropertyViewTypeCacheTransfer','TestPropertyViewReentrantTypeMaterialization','TestPropertyViewTypeIndependentHistories','TestPropertyViewNestedQueryAssignment','TestPropertyViewPanicHistory'}
assert [r['name'] for r in report['results']]==['normal','race','checkptr']
for r in report['results']:
 assert r['exitCode']==0 and set(r['passed'])==expected
 events=[json.loads(x) for x in (p/(r['name']+'.stdout')).read_text().splitlines()]
 assert not any(e['Action'] in ['fail','skip'] for e in events)
 assert {e['Test'] for e in events if e['Action']=='pass' and 'Test' in e}==expected
 assert any(e['Action']=='pass' and 'Test' not in e for e in events)
(p/'readback.json').write_text(json.dumps({'passed':True,'sources':report['sources'],'files':{f.name:sha(f) for f in sorted(p.iterdir()) if f.is_file() and f.name not in ['readback.json','manifest.json']}},indent=2)+'\n')
print('Raw normal/race/checkptr evidence and staged source hashes verified')
