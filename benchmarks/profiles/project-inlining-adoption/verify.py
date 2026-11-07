from pathlib import Path
import hashlib,json,struct,subprocess
root=Path(__file__).resolve().parents[3]
old=Path('/tmp/tsc-project-inlining-validation/tsc-go-project-inlining')
new=root/'packages/tsc-go/dist/tsc-go'
sha=lambda b:hashlib.sha256(b).hexdigest()
a=json.loads(Path(str(old)+'.provenance.json').read_text());b=json.loads(Path(str(new)+'.provenance.json').read_text())
assert sha(old.read_bytes())=='861bb976759b424b299f80489e6907cf6f36e9ea7e393a9a33c3be0108541f46'
assert a['build']==b['build']
af={f['path']:f for f in a['source']['files']};bf={f['path']:f for f in b['source']['files']}
assert af.keys()==bf.keys()
changed=[p for p in af if af[p]!=bf[p]]
assert changed==['packages/tsc-go/scripts/build.mjs'],changed

def sections(path):
 data=path.read_bytes();assert data[:6]==b'\x7fELF\x02\x01'
 off=struct.unpack_from('<Q',data,40)[0];size,n,si=struct.unpack_from('<HHH',data,58)
 headers=[struct.unpack_from('<IIQQQQIIQQ',data,off+i*size) for i in range(n)]
 h=headers[si];names=data[h[4]:h[4]+h[5]]
 return {names[h[0]:].split(b'\0')[0].decode():(h,data[h[4]:h[4]+h[5]] if h[1]!=8 else b'') for h in headers}
sa,sb=sections(old),sections(new);assert sa.keys()==sb.keys()
versions=[subprocess.check_output(['/tmp/tsc-toolchains/go/bin/go','version','-m',str(p)],text=True).splitlines()[1:] for p in [old,new]]
replacements=[]
for x,y in zip(*versions,strict=True):
 if x!=y:
  assert any(x.startswith('\tbuild\t'+k+'=') and y.startswith('\tbuild\t'+k+'=') for k in ['vcs.revision','vcs.time'])
  replacements.append((x.split('=',1)[1].encode(),y.split('=',1)[1].encode()))
rows=[]
for name,(header,data) in sa.items():
 other_header,other=sb[name];assert header==other_header,name
 if name in ['.note.go.buildid','.note.gnu.build-id']:
  kind='build identifier'
 else:
  normalized=data
  for x,y in replacements: normalized=normalized.replace(x,y)
  assert normalized==other,name
  kind='identical' if data==other else 'only embedded vcs revision/time'
 rows.append({'section':name,'comparison':kind,'validatedSha256':sha(data),'productionSha256':sha(other)})
for direction in ['forward','reverse']:
 p=json.loads((root/f'benchmarks/results/project-inlining-confirm-{direction}/recording/proposal.json').read_text())
 assert p['passesThisConfirmation'] and all(p['gates'].values())
report={'passed':True,'productionBinarySha256':sha(new.read_bytes()),'productionSidecarSha256':sha(Path(str(new)+'.provenance.json').read_bytes()),'productionSourceSha256':b['source']['sha256'],'sourceManifestChanges':changed,'sections':rows,'scope':'All ELF sections equal except build IDs and explicitly normalized VCS revision/time. Compiler sources and build settings match fully validated candidate.'}
(root/'benchmarks/profiles/project-inlining-adoption/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sections'},indent=2))
