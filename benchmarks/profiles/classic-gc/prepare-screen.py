"""Finalize config only after collector correctness readback."""
from pathlib import Path
import hashlib,json,copy
profile=Path(__file__).resolve().parent;root=profile.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
build=json.loads((profile/'build.json').read_text());assert build['passed']
assert json.loads((profile/'readback.json').read_text())['passed']
config=json.loads((profile.parent/'lazy-identifier-names/screen.json').read_text())
config['name']='classic-gc'
expected=config['expected']['candidate']
expected.update(path=build['binary'],sha256=build['binarySha256'],source=build['sourceSha256'],sidecarSha256=build['sidecarSha256'],revisionLabel='Classic collector')
metadata=[]
for side in ['baseline','candidate']:
 e=config['expected'][side];binary=Path(e['path']);sidecar=Path(str(binary)+'.provenance.json')
 assert sha(binary)==e['sha256'] and sha(sidecar)==e['sidecarSha256']
 metadata.append(json.loads(sidecar.read_text()))
a,b=metadata;normalized=copy.deepcopy(b['build'])
assert a['build']['toolchain']['GOEXPERIMENT']=='' and normalized['toolchain']['GOEXPERIMENT']=='nogreenteagc'
normalized['toolchain']['GOEXPERIMENT']='';assert a['build']==normalized
assert a['source']['sha256']==b['source']['sha256']==build['sourceSha256']
assert a['source']['files']==b['source']['files']
config.update(sourceDifference=[],sourceCounts={'baseline':len(a['source']['files']),'candidate':len(b['source']['files'])},buildDifference={'GOEXPERIMENT':{'baseline':'','candidate':'nogreenteagc'}},workspaceSource=build['sourceSha256'],comparisonPolicySha256=sha(profile/'COMPARISON_POLICY.md'),methodology='Fresh-process/default-runtime matched GNU-time RSS collector screen; candidate built GOEXPERIMENT=nogreenteagc, all other recorded build settings identical; pinned physical inputs; no timing during validation/build/Git work.')
with (profile/'screen.json').open('x') as f:f.write(json.dumps(config,indent=2)+'\n')
print(json.dumps({'source':build['sourceSha256'],'binary':expected['sha256'],'buildDifference':config['buildDifference']}))
