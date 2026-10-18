from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3];profile=Path(__file__).resolve().parent
out=root/'benchmarks/results/direct-reference-confirm-forward';execution=out/'execution';execution.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((out/'summary.json').read_text());d=json.loads((out/'recording/partial-decision.json').read_text())
assert s['status']=='failed' and d['failedFloors']==['typeorm','trpc']
assert sha(out/'summary.json')==d['summarySha256']
files={root/k:v for k,v in s['snapshot']['files'].items()};files.update({Path(k):v for k,v in s['controllerFiles'].items()})
for name in ['record-interrupted.mjs','confirmation-stats.mjs']:
 f=profile/name;files[f]=sha(f)
manifest=[]
def copy(src,rel,digest):
 assert sha(src)==digest
 dst=execution/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 assert sha(dst)==digest
 manifest.append({'path':str(rel),'sha256':digest,'bytes':dst.stat().st_size})
for src,digest in files.items():copy(src,src.relative_to(root),digest)
supervisor=Path('/tmp/tsc-direct-reference-confirm-forward-supervisor.jsonl')
events=[json.loads(x) for x in supervisor.read_text().splitlines()]
assert events[-1]['event']=='exited' and events[-1]['returnCode']==143
assert any(x.get('event')=='signal' and x.get('signal')==15 for x in events)
copy(supervisor,Path('supervisor.jsonl'),sha(supervisor))
(execution/'manifest.json').write_text(json.dumps({'files':manifest,'allCopiesReadBackVerified':True},indent=2)+'\n')
for f in manifest:assert sha(execution/f['path'])==f['sha256']
rows=(out/'recording/PERF.rows.md').read_text();assert len(rows.splitlines())==2
perf=root/'PERF.md';text=perf.read_text();assert 'Direct scalar reference flags incomplete confirmation 1' not in text
perf.write_text(text+rows)
assert all(not x.strip() or x.startswith('|') for x in perf.read_text().splitlines())
print('Archived',len(manifest),'execution files; appended two independently verified partial-confirmation rows')
