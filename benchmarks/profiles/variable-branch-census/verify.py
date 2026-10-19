from pathlib import Path
import hashlib,json,subprocess
from counts import validate
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 r=json.loads((P/'report-resumed.json').read_text());assert r['status']=='passed'
 original=json.loads((P/'report.json').read_text())
 assert original['status']=='failed' and original['error']=='SystemExit(143)'
 assert sha(P/'report.json')==r['originalReportSha256']
 assert original['controllerSha256']==sha(P/'capture.py')
 assert r['completedPrefixCount']==14 and r['runs'][:14]==original['runs']
 for key in ['baseHead','baseSource','baselineSha256','baselineSidecarSha256','candidateSha256','overlaySources','countsValidatorSha256','validationSha256','buildReportSha256']:
  assert r[key]==original[key],key
 for field,file in [('controllerSha256','capture-remaining.py'),('countsValidatorSha256','counts.py'),('validationSha256','validation.json'),('buildReportSha256','build.json')]:assert sha(P/file)==r[field]
 overlay=json.loads((P/'overlay.json').read_text())['Replace'];sources={k:sha(v) for k,v in overlay.items()};assert sources==r['overlaySources']
 v=json.loads((P/'validation.json').read_text());assert v['status']=='passed' and v['sources']==sources
 expected={'TestVariableBranchNestedPartition','TestVariableBranchAnnotationDifferential','TestVariableBranchSnapshotFields'}
 for mode in ['normal','race','checkptr']:
  events=[json.loads(x) for x in (P/(mode+'.stdout')).read_text().splitlines()]
  assert {e['Test'] for e in events if e['Action']=='pass' and 'Test' in e}==expected
  assert not any(e['Action'] in ['fail','skip'] for e in events)
  assert any(e['Action']=='pass' and 'Test' not in e for e in events)
 baseline=ROOT/'packages/tsc-go/dist/tsc-go-node-pointer';candidate=Path('/tmp/tsc-variable-branch-census')
 assert sha(baseline)==r['baselineSha256'] and sha(str(baseline)+'.provenance.json')==r['baselineSidecarSha256'] and sha(candidate)==r['candidateSha256']
 js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
 source=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=ROOT,text=True));assert source['sha256']==r['baseSource'] and source['revision']==r['baseHead']
 assert [(x['project'],x['checkers'],x['mode']) for x in r['runs']]==[(p,c,m) for p in ['typeorm','trpc','vscode','sentry'] for c in [1,4] for m in ['baseline','disabled','enabled']]
 for run in r['runs']:
  ref=ROOT/run['reference'];assert sha(ref)==run['referenceSha256']
  project=next(x for x in json.loads(ref.read_text())['projects'] if x['name']==run['project'])
  assert run['exitStatus']==0 and run['cwd']==project['cwd'] and run['inputCount']==len(project['preflight']['candidate']['inputs'])
  assert run['command']==[str(baseline if run['mode']=='baseline' else candidate),*project['args'],'--checkers',str(run['checkers'])]
  assert sha(Path(project['cwd'])/project['args'][1])==project['configSha256']
  for item in project['preflight']['candidate']['inputs']:assert sha(Path(project['cwd'])/item['file'])==item['sha256']
  work=P/run['project']
  for suffix in ['stdout','stderr']:
   file=work/(str(run['checkers'])+'-'+run['mode']+'.'+suffix);assert file.read_bytes()==b'' and sha(file)==run[suffix+'Sha256']
  if run['mode']!='enabled':assert run['artifacts']=={} and run['counts'] is None;continue
  name=str(run['checkers'])+'-census.json';assert list(run['artifacts'])==[name]
  file=work/name;meta=run['artifacts'][name];assert sha(file)==meta['sha256'] and file.stat().st_size==meta['bytes']
  assert validate(json.loads(file.read_text()))==run['counts']
 (P/'readback.json').write_text(json.dumps({'passed':True,'reportSha256':sha(P/'report-resumed.json'),'verifierSha256':sha(__file__),'sources':sources},indent=2)+'\n')
 print('Verified 24 controls, eight uncapped branch snapshots, focused logs and frozen provenance.')
if __name__=='__main__':main()
