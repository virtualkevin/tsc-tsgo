"""Create benchmark config only after a normal provenance-backed build exists."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3]
profile=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# These files intentionally do not use the diagnostic overlay build metadata.
build=json.loads((profile/'production-build.json').read_text())
assert build['passed'] and build['retainedSourceAndDefaultRestored']
assert json.loads((profile/'cli-readback.json').read_text())['passed']
assert json.loads((profile/'full-readback.json').read_text())['passed']
source=json.loads((profile/'production-source.json').read_text())
freeze=json.loads((profile/'cli-freeze.json').read_text())
freeze['overlaySources']={str(Path(k).relative_to(root/'packages/tsc-go')):v for k,v in freeze['sources'].items()}
config=json.loads((profile.parent/'lazy-identifier-names/screen.json').read_text())
config['name']='reduction-scratch-candidate'
config['expected']['baseline'].update(path=str(root/'packages/tsc-go/dist/tsc-go'),sha256='9017fa9abe7add6cadf8cefffca2aea161938b63aeac46ed8d226d7dca916d2a',source='b50f489f20634bf3570a18d0fcc5cf811036fbcefe2a5ea481b193f848768445',sidecarSha256='5164f58805236585d39258604fb12e274475039d04fd3efd5b8572d84c2cf287',revisionLabel='Retained project-inlining Go')
expected=config['expected']['candidate']
expected.update(path=str(root/'packages/tsc-go/dist/tsc-go-reduction-scratch'),sha256=build['binarySha256'],source=source['sha256'],sidecarSha256=build['sidecarSha256'],revisionLabel='Reduction scratch reuse')
metadata=[]
for side in ['baseline','candidate']:
 e=config['expected'][side];binary=Path(e['path']);sidecar=Path(str(binary)+'.provenance.json')
 assert sha(binary)==e['sha256'] and sha(sidecar)==e['sidecarSha256']
 metadata.append(json.loads(sidecar.read_text()))
assert metadata[0]['build']==metadata[1]['build']
assert metadata[1]['source']['sha256']==source['sha256']
before={f['path']:f for f in metadata[0]['source']['files']};after={f['path']:f for f in metadata[1]['source']['files']}
delta=[{'path':path,'before':before.get(path),'after':after.get(path)} for path in sorted(set(before)|set(after)) if before.get(path)!=after.get(path)]
assert len(delta)==3
assert {d['path'] for d in delta}=={'packages/tsc-go/'+rel for rel in freeze['overlaySources']}
for d in delta:assert d['after']['sha256']==freeze['overlaySources'][d['path'].removeprefix('packages/tsc-go/')]
config.update(sourceDifference=delta,sourceCounts={'baseline':len(before),'candidate':len(after)},workspaceSource='b50f489f20634bf3570a18d0fcc5cf811036fbcefe2a5ea481b193f848768445',comparisonPolicySha256=sha(profile/'COMPARISON_POLICY.md'),methodology='Fresh-process/default-runtime matched GNU-time RSS screen of reduction scratch reuse on pinned physical inputs; no timing during validation/build/Git work.')
(profile/'screen.json').write_text(json.dumps(config,indent=2)+'\n')
print(json.dumps({'source':source['sha256'],'binary':expected['sha256'],'sourceCounts':config['sourceCounts'],'changedFiles':len(delta)}))
