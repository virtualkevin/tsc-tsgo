from pathlib import Path
import json,hashlib,subprocess,gzip
from counts import validate
from artifacts import read_capture,digest
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((out/'report-resumed.json').read_text());assert r['status']=='passed'
original=json.loads((out/'report.json').read_text());assert sha(out/'report.json')==r['originalReportSha256']
assert original['status']=='failed' and original['error']=='SystemExit(143)'
assert r['completedPrefixCount']==len(original['runs'])==13 and r['runs'][:13]==original['runs']
assert sha(out/'capture.py')==original['controllerSha256']
assert sha(out/'capture-remaining.py')==r['controllerSha256'];assert sha(out/'counts.py')==r['countsValidatorSha256']
assert sha(out/'validation.json')==r['validationSha256'] and sha(out/'build.json')==r['buildReportSha256']
overlay=json.loads((out/'overlay.json').read_text())['Replace'];assert r['overlaySources']=={k:sha(v) for k,v in overlay.items()}
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
s=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True));assert s['sha256']==r['baseSource'] and s['revision']==r['baseHead']
baseline=root/'packages/tsc-go/dist/tsc-go-node-pointer';candidate=Path('/tmp/tsc-symbol-resolution-census')
assert sha(baseline)==r['baselineSha256'] and sha(candidate)==r['candidateSha256'] and sha(str(baseline)+'.provenance.json')==r['baselineSidecarSha256']
assert len(r['runs'])==24
assert [(x['project'],x['checkers'],x['mode']) for x in r['runs']]==[(p,c,m) for p in ['typeorm','trpc','vscode','sentry'] for c in [1,4] for m in ['baseline','disabled','enabled']]
for run in r['runs']:
 ref=root/run['reference'];assert sha(ref)==run['referenceSha256']
 p=next(x for x in json.loads(ref.read_text())['projects'] if x['name']==run['project'])
 assert run['cwd']==p['cwd'] and run['inputCount']==len(p['preflight']['candidate']['inputs'])
 assert run['command']==[str(baseline if run['mode']=='baseline' else candidate),*p['args'],'--checkers',str(run['checkers'])]
 assert sha(Path(p['cwd'])/p['args'][1])==p['configSha256']
 for x in p['preflight']['candidate']['inputs']:assert sha(Path(p['cwd'])/x['file'])==x['sha256']
 work=out/run['project'];assert run['exitStatus']==0
 for suffix in ['stdout','stderr']:
  f=work/(str(run['checkers'])+'-'+run['mode']+'.'+suffix);assert sha(f)==run[suffix+'Sha256'] and f.read_bytes()==b''
 if run['mode']!='enabled':assert run['artifacts']=={} and run['counts'] is None;continue
 name=str(run['checkers'])+'-census.json'
 assert list(run['artifacts'])==[name]
 f=work/name;v=run['artifacts'][name];data=read_capture(f);assert digest(data)==v['sha256'] and len(data)==v['bytes']
 assert validate(json.loads(data))==run['counts']
archive_manifest=out/'archive-manifest.json'
if archive_manifest.exists():
 archive=json.loads(archive_manifest.read_text());assert archive['readBackVerified'] and len(archive['files'])==8
 expected={str(Path(run['project'])/name)+'.gz':meta for run in r['runs'] for name,meta in run['artifacts'].items()}
 assert {f['path'] for f in archive['files']}==set(expected)
 for entry in archive['files']:
  compressed=(out/entry['path']).read_bytes();raw=gzip.decompress(compressed);meta=expected[entry['path']]
  assert digest(compressed)==entry['sha256'] and len(compressed)==entry['bytes']
  assert digest(raw)==entry['rawSha256']==meta['sha256'] and len(raw)==entry['rawBytes']==meta['bytes']
print('Verified 24 controls, eight census snapshots, reconciled events, exact inputs and frozen source/binary/controller provenance')
