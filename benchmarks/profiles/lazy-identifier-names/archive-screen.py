from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3];out=root/'benchmarks/results/lazy-identifier-names-screen';execution=out/'execution';execution.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=json.loads((out/'summary.json').read_text());p=json.loads((out/'recording/proposal.json').read_text())
assert s['status']=='passed' and p['status']=='passed' and not p['qualifiesForConfirmation']
files={root/k:v for k,v in s['snapshot']['files'].items()}
files.update({Path(k):v for k,v in s['controllerFiles'].items()})
manifest=[]
def copy(src,rel,expected):
 assert sha(src)==expected
 dst=execution/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(dst)==expected
 manifest.append({'path':str(rel),'sha256':expected,'bytes':dst.stat().st_size})
for src,h in files.items():copy(src,src.relative_to(root),h)
recorder=root/'benchmarks/profiles/lazy-identifier-names/record-screen.mjs';copy(recorder,recorder.relative_to(root),sha(recorder))
for name in ['screen.stdout','screen.stderr','record.stdout','record.stderr']:
 src=Path('/tmp/tsc-lazy-identifier-names')/name;copy(src,Path(name),sha(src))
(execution/'manifest.json').write_text(json.dumps({'files':manifest,'allCopiesReadBackVerified':True},indent=2)+'\n')
for f in json.loads((execution/'manifest.json').read_text())['files']:assert sha(execution/f['path'])==f['sha256']
rows=(out/'recording/PERF.rows.md').read_text();assert len(rows.splitlines())==4
perf=root/'PERF.md';text=perf.read_text();assert 'Lazy identifier names versus retained node-pointer Go' not in text
perf.write_text(text+rows)
assert all(not line.strip() or line.startswith('|') for line in perf.read_text().splitlines())
print('Archived and readback verified',len(manifest),'execution files; appended four PERF rows')
