from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3];base=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((base/'build.json').read_text());source=json.loads(Path('/tmp/tsc-runtime-small-string/source.json').read_text())
assert source['sha256']=='216d40c773062d193391ca6a7ccced033224047aa8f75f656e19b999d0b764cd'
c=json.loads((base.parent/'mapper-pair/screen.json').read_text());c['name']='runtime-small-string'
e=c['expected']['candidate'];e.update(path=str(root/'packages/tsc-go/dist/tsc-go-runtime-small-string'),sha256=build['binarySha256'],source=source['sha256'],sidecarSha256=build['sidecarSha256'],revisionLabel='Small string-map runtime matching')
meta=[]
for e in c['expected'].values():
 p=Path(e['path']);assert sha(p)==e['sha256'];assert sha(Path(str(p)+'.provenance.json'))==e['sidecarSha256'];meta.append(json.loads(Path(str(p)+'.provenance.json').read_text()))
assert meta[0]['source']['files']==meta[1]['source']['files']
flags=hashlib.sha256(build['goFlags'].encode()).hexdigest()
a=meta[0]['build'].copy();a.update(extraFlagsPresent=True,extraFlagsSha256=flags);assert a==meta[1]['build']
c.update(sourceDifference=[],sourceCounts=dict(baseline=len(source['files']),candidate=len(source['files'])),workspaceSource=source['sha256'],comparisonPolicySha256=sha(base/'COMPARISON_POLICY.md'),runtimeInputs=build['runtimeInputs'],overlaySha256=build['overlaySha256'],overlayFlagsSha256=flags)
c['methodology']='Frozen small-string-map runtime overlay versus retained unmodified runtime; identical compiler source, explicit hashed overlay build difference; nine small/five large alternating pairs, one warmup, default settings, matched RSS, identical physical inputs. Full correctness and two independent confirmations before retention.'
(base/'screen.json').write_text(json.dumps(c,indent=2)+'\n')
build['sourceSha256']=source['sha256'];(base/'build.json').write_text(json.dumps(build,indent=2)+'\n');Path('/tmp/tsc-runtime-small-string/build.json').write_text(json.dumps(build,indent=2)+'\n')
print(json.dumps(dict(source=source['sha256'],binary=build['binarySha256'],overlayFlagsSha256=flags)))
