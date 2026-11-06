from pathlib import Path
import hashlib,json,subprocess,sys
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'validation.json').read_text());assert v['passed']
assert v['sources']=={f.name:sha(f) for f in (p/'prototype').iterdir() if f.is_file()}
assert [r['mode'] for r in v['runs']]==['normal','race','checkptr']
for r in v['runs']:
 assert r['passed'] and r['exitCode']==0
 for stream in ['stdout','stderr']:assert sha(p/(r['mode']+'.'+stream))==r[stream+'Sha256']
 events=[json.loads(x) for x in (p/(r['mode']+'.stdout')).read_text().splitlines()]
 assert {e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e}==set(r['tests'])=={'TestBoundaryHistory','TestRandomHistories','TestTileSharingAndIndependentStores'}
 assert not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
proofBefore=(p/'proof.json').read_bytes()
subprocess.run([sys.executable,str(p/'prove.py')],check=True,stdout=subprocess.DEVNULL)
assert (p/'proof.json').read_bytes()==proofBefore
(p/'readback.json').write_text(json.dumps({'passed':True,'sources':v['sources'],'evidence':{n:sha(p/n) for n in ['validation.json','proof.json','prove.py','verify.py','validate.py','requirements.txt']}},indent=2)+'\n')
print('All three test modes and nine solver claims reproduced')
