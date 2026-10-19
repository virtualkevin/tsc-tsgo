from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'validation.json').read_text())
s=json.loads((p/'overlay.json').read_text())['Replace']
assert v['status']=='passed' and v['sources']=={k:sha(f) for k,f in s.items()}
expected=None
for result in v['results']:
 name=result['name']
 rows=[json.loads(line) for line in (p/(name+'.stdout')).read_text().splitlines()]
 passed=[r['Test'] for r in rows if r.get('Action')=='pass' and 'Test' in r]
 assert len(passed)==15 and len(set(passed))==15 and passed==result['passed']
 assert result['exitCode']==0 and not any(r.get('Action') in ('fail','skip') for r in rows)
 assert any(r.get('Action')=='pass' and 'Test' not in r for r in rows)
 if expected is None:expected=set(passed)
 assert set(passed)==expected
assert [r['name'] for r in v['results']]==['normal','race','checkptr']
files=sorted(f for f in p.rglob('*') if f.is_file() and f.name!='readback.json')
(p/'readback.json').write_text(json.dumps({'status':'passed','testsPerMode':15,'files':{str(f.relative_to(p)):sha(f) for f in files}},indent=2)+'\n')
print('Verified 15 focused tests in each of normal, race, and checkptr modes; source hashes match.')
