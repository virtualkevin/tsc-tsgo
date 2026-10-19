from pathlib import Path
import json,hashlib,subprocess
from counts import validate
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((out/'report.json').read_text());assert r['status']=='passed'
assert sha(out/'capture.py')==r['controllerSha256'];assert sha(out/'counts.py')==r['countsValidatorSha256']
assert sha(out/'validation.json')==r['validationSha256'] and sha(out/'build.json')==r['buildReportSha256']
overlay=json.loads((out/'overlay.json').read_text())['Replace'];assert r['overlaySources']=={k:sha(v) for k,v in overlay.items()}
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
s=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True));assert s['sha256']==r['baseSource'] and s['revision']==r['baseHead']
baseline=root/'packages/tsc-go/dist/tsc-go-property-relation-snapshot';candidate=Path('/tmp/tsc-property-view-census')
assert sha(baseline)==r['baselineSha256'] and sha(candidate)==r['candidateSha256'] and sha(str(baseline)+'.provenance.json')==r['baselineSidecarSha256']
assert len(r['runs'])==12
assert [(x['project'],x['mode']) for x in r['runs']]==[(p,m) for p in ['typeorm','trpc','vscode','sentry'] for m in ['baseline','disabled','enabled']]
for run in r['runs']:
 ref=root/run['reference'];assert sha(ref)==run['referenceSha256']
 p=next(x for x in json.loads(ref.read_text())['projects'] if x['name']==run['project'])
 assert run['cwd']==p['cwd'] and run['inputCount']==len(p['preflight']['candidate']['inputs'])
 assert run['command']==[str(baseline if run['mode']=='baseline' else candidate),*p['args']]
 assert sha(Path(p['cwd'])/p['args'][1])==p['configSha256']
 for x in p['preflight']['candidate']['inputs']:assert sha(Path(p['cwd'])/x['file'])==x['sha256']
 work=out/run['project'];assert run['exitStatus']==0
 for suffix in ['stdout','stderr']:
  f=work/(run['mode']+'.'+suffix);assert sha(f)==run[suffix+'Sha256'] and f.read_bytes()==b''
 if run['mode']!='enabled':assert run['artifacts']=={} and run['counts'] is None;continue
 assert list(run['artifacts'])==['census.json']
 f=work/'census.json';v=run['artifacts']['census.json'];assert sha(f)==v['sha256'] and f.stat().st_size==v['bytes']
 assert validate(json.loads(f.read_text()))==run['counts']
print('Verified twelve controls, four census records, category totals, exact inputs and frozen source/binary/controller provenance')
