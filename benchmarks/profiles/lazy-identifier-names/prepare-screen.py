from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[3];base=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((base/'build.json').read_text());source=json.loads((base/'source.json').read_text())
assert source['sha256']=='babf18329923e53e653076216420ff75d339bd093f24d65fc088fcc54b67b247'
c=json.loads((base.parent/'pending-member-index/screen.json').read_text());c['name']='lazy-identifier-names'
e=c['expected']['candidate'];e.update(path=str(root/'packages/tsc-go/dist/tsc-go-lazy-identifier-names'),sha256=build['binarySha256'],source=source['sha256'],sidecarSha256=build['sidecarSha256'],revisionLabel='Lazy identifier names')
meta=[]
for key in ['baseline','candidate']:
 e=c['expected'][key];p=Path(e['path']);assert sha(p)==e['sha256'];assert sha(Path(str(p)+'.provenance.json'))==e['sidecarSha256'];meta.append(json.loads(Path(str(p)+'.provenance.json').read_text()))
assert meta[0]['build']==meta[1]['build'];assert meta[1]['source']['sha256']==source['sha256']
a={f['path']:f for f in meta[0]['source']['files']};b={f['path']:f for f in meta[1]['source']['files']}
c['sourceDifference']=[dict(path=p,before=a.get(p),after=b.get(p)) for p in sorted(set(a)|set(b)) if a.get(p)!=b.get(p)]
assert len(c['sourceDifference'])==5
c['sourceCounts']=dict(baseline=len(a),candidate=len(b));c['workspaceSource']=source['sha256'];c['comparisonPolicySha256']=sha(base/'COMPARISON_POLICY.md');c['methodology']=c['methodology'].replace('indexed pending-member cache','lazy identifier names')
(base/'screen.json').write_text(json.dumps(c,indent=2)+'\n')
build['sourceSha256']=source['sha256'];(base/'build.json').write_text(json.dumps(build,indent=2)+'\n');Path('/tmp/tsc-lazy-identifier-names/build.json').write_text(json.dumps(build,indent=2)+'\n')
print(json.dumps(dict(source=source['sha256'],binary=build['binarySha256'],sourceCounts=c['sourceCounts'])))
