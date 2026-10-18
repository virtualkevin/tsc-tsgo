"""Restore only verified candidate paths from the pre-application baseline backup."""
from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parents[3];profile=Path(__file__).resolve().parent
module=root/'packages/tsc-go'
sha=lambda b:hashlib.sha256(b).hexdigest()
meta=json.loads((profile/'baseline-source-backup.json').read_text())
freeze=json.loads((profile/'final-freeze.json').read_text())
assert len(meta['files'])==2
assert {x['path']:x['candidateSha256'] for x in meta['files']}==freeze['overlaySources']
assert not (profile/'restoration.json').exists()
changes=[]
for item in meta['files']:
 rel=Path(item['path']);assert not rel.is_absolute() and '..' not in rel.parts
 dest=module/rel;assert sha(dest.read_bytes())==item['candidateSha256']
 data=None
 if item['before']:
  data=(Path(meta['directory'])/rel).read_bytes();assert sha(data)==item['before']['sha256']
 changes.append((dest,data,item['before']))
# All 2 destination and backup hashes have passed before any mutation.
for dest,data,before in changes:
 if data is None:dest.unlink()
 else:dest.write_bytes(data);os.chmod(dest,before['mode'])
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
source=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True))
assert source['sha256']==meta['baselineSourceSha256']
retained={'tsc-go':'8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f','tsc-go.provenance.json':'76e6c4f05d244f4f3f1cd562950bbc3388716b139176ee3583ecc912e3a2bca2'}
for name,h in retained.items():assert sha((module/'dist'/name).read_bytes())==h
config_path=profile/'screen.json'
if config_path.exists():
 config=json.loads(config_path.read_text());config['workspaceSource']=source['sha256'];config_path.write_text(json.dumps(config,indent=2)+'\n')
report={'passed':True,'sourceSha256':source['sha256'],'files':len(source['files']),'restoredPaths':len(changes),'retainedDefault':retained}
(profile/'restoration.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
