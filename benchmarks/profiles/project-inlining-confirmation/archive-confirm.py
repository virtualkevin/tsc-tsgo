from pathlib import Path
import hashlib,json,shutil,sys
root=Path(__file__).resolve().parents[3];mode=sys.argv[1];assert mode in ['forward','reverse']
r=root/('benchmarks/results/project-inlining-confirm-'+mode);s=json.loads((r/'summary.json').read_text());p=json.loads((r/'recording/proposal.json').read_text());assert s['status']==p['status']=='passed'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert p['summarySha256']==sha(r/'summary.json')
e=r/'execution';e.mkdir();files={root/k:v for k,v in s['snapshot']['files'].items()};files.update({Path(k):v for k,v in s['controllerFiles'].items()})
profile=Path(__file__).resolve().parent
for name,key in [('record-confirm.mjs','recorderSha256'),('confirmation-stats.mjs','statsModuleSha256')]:files[profile/name]=p[key]
manifest=[]
for src,h in files.items():
 assert sha(src)==h;rel=src.relative_to(root);dst=e/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);assert sha(dst)==h;manifest.append({'path':str(rel),'sha256':h})
src=Path('/tmp/tsc-project-inlining-confirm-'+mode+'-supervisor.jsonl');events=[json.loads(x) for x in src.read_text().splitlines()];assert events[-1]['event']=='exited' and events[-1]['returnCode']==0
shutil.copyfile(src,e/'supervisor.jsonl');assert sha(src)==sha(e/'supervisor.jsonl');manifest.append({'path':'supervisor.jsonl','sha256':sha(src)})
(e/'manifest.json').write_text(json.dumps({'files':manifest,'allCopiesReadBackVerified':True},indent=2)+'\n')
rows=(r/'recording/PERF.rows.md').read_text();assert len(rows.splitlines())==4
perf=root/'PERF.md';text=perf.read_text();assert rows not in text;perf.write_text(text+rows)
print('Archived',len(manifest),'execution files and appended four PERF rows')
