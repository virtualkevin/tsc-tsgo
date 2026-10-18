from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3];base=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((base/'build.json').read_text());source=json.loads(Path('/tmp/tsc-merged-symbol-filter/source.json').read_text())
assert source['sha256']=='e080bdefda682bc104587228e894f74321f02c3ef699d811d30aa9c4f04d315b'
c=json.loads((base.parent/'pending-member-index/screen.json').read_text());c['name']='merged-symbol-filter'
e=c['expected']['candidate'];e.update(path=str(root/'packages/tsc-go/dist/tsc-go-merged-symbol-filter'),sha256=build['binarySha256'],source=source['sha256'],sidecarSha256=build['sidecarSha256'],revisionLabel='Merged-symbol membership filter')
meta=[]
for key in ['baseline','candidate']:
 e=c['expected'][key];p=Path(e['path']);assert sha(p)==e['sha256'];assert sha(Path(str(p)+'.provenance.json'))==e['sidecarSha256'];meta.append(json.loads(Path(str(p)+'.provenance.json').read_text()))
assert meta[0]['build']==meta[1]['build'];assert meta[1]['source']['sha256']==source['sha256']
a={f['path']:f for f in meta[0]['source']['files']};b={f['path']:f for f in meta[1]['source']['files']}
c['sourceDifference']=[dict(path=p,before=a.get(p),after=b.get(p)) for p in sorted(set(a)|set(b)) if a.get(p)!=b.get(p)]
assert [x['path'] for x in c['sourceDifference']]==['packages/tsc-go/internal/checker/checker.go','packages/tsc-go/internal/checker/merged_symbol_filter_test.go','packages/tsc-go/internal/core/pointerfilter.go','packages/tsc-go/internal/core/pointerfilter_test.go']
c['sourceCounts']=dict(baseline=len(a),candidate=len(b));c['workspaceSource']=source['sha256'];c['comparisonPolicySha256']=sha(base/'COMPARISON_POLICY.md');c['methodology']=c['methodology'].replace('indexed pending-member cache','merged-symbol membership filter')
(base/'screen.json').write_text(json.dumps(c,indent=2)+'\n')
build['sourceSha256']=source['sha256'];(base/'build.json').write_text(json.dumps(build,indent=2)+'\n');Path('/tmp/tsc-merged-symbol-filter/build.json').write_text(json.dumps(build,indent=2)+'\n')
focused=Path('/tmp/tsc-merged-symbol-filter/focused.jsonl');events=[json.loads(x) for x in focused.read_text().splitlines()];terminal=[x for x in events if x['Action'] in ['pass','fail','skip']];assert all(x['Action']=='pass' for x in terminal)
assert len([x for x in terminal if 'Test' in x])==4 and len([x for x in terminal if 'Test' not in x])==2
shutil.copyfile(focused,base/'focused.jsonl')
print(json.dumps(dict(source=source['sha256'],binary=build['binarySha256'],sourceCounts=c['sourceCounts'],focusedTests=4)))
