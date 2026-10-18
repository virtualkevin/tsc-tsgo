"""Create benchmark config only after a normal provenance-backed build exists."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3]
profile=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# These files intentionally do not use the diagnostic overlay build metadata.
build=json.loads((profile/'production-build.json').read_text())
source=json.loads((profile/'production-source.json').read_text())
freeze=json.loads((profile/'final-freeze.json').read_text())
config=json.loads((profile.parent/'lazy-identifier-names/screen.json').read_text())
config['name']='declaration-cache'
expected=config['expected']['candidate']
expected.update(path=str(root/'packages/tsc-go/dist/tsc-go-declaration-cache'),sha256=build['binarySha256'],source=source['sha256'],sidecarSha256=build['sidecarSha256'],revisionLabel='Completed declaration diagnostic reuse')
metadata=[]
for side in ['baseline','candidate']:
 e=config['expected'][side];binary=Path(e['path']);sidecar=Path(str(binary)+'.provenance.json')
 assert sha(binary)==e['sha256'] and sha(sidecar)==e['sidecarSha256']
 metadata.append(json.loads(sidecar.read_text()))
assert metadata[0]['build']==metadata[1]['build']
assert metadata[1]['source']['sha256']==source['sha256']
before={f['path']:f for f in metadata[0]['source']['files']};after={f['path']:f for f in metadata[1]['source']['files']}
delta=[{'path':path,'before':before.get(path),'after':after.get(path)} for path in sorted(set(before)|set(after)) if before.get(path)!=after.get(path)]
assert len(delta)==2
assert {d['path'] for d in delta}=={'packages/tsc-go/'+rel for rel in freeze['overlaySources']}
for d in delta:assert d['after']['sha256']==freeze['overlaySources'][d['path'].removeprefix('packages/tsc-go/')]
config.update(sourceDifference=delta,sourceCounts={'baseline':len(before),'candidate':len(after)},workspaceSource=source['sha256'],comparisonPolicySha256=sha(profile/'COMPARISON_POLICY.md'),methodology='Fresh-process/default-runtime matched GNU-time RSS screen of completed declaration diagnostic reuse on pinned physical inputs; no timing during validation/build/Git work.')
(profile/'screen.json').write_text(json.dumps(config,indent=2)+'\n')
print(json.dumps({'source':source['sha256'],'binary':expected['sha256'],'sourceCounts':config['sourceCounts'],'changedFiles':len(delta)}))
