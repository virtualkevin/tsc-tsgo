from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent;R=P.parents[2]
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
report=json.loads((P/'report.json').read_text());assert report['status']=='passed'
assert sha(P/'capture.py')==report['controllerSha256']
assert sha(P/'validation.json')==report['validationSha256']
assert sha(P/'build.json')==report['buildReportSha256']
validation=json.loads((P/'validation.json').read_text())
assert validation['status']=='passed' and validation['sources']==report['overlaySources']
assert [r['name'] for r in validation['results']]==['normal','race','checkptr']
expected={'TestSymbolColdCensusMasks','TestSymbolColdCensusSampling','TestSymbolColdCensusConcurrentLedger'}
for run in validation['results']:
 assert run['exitCode']==0 and set(run['passed'])==expected
 events=[json.loads(l) for l in (P/(run['name']+'.stdout')).read_text().splitlines()]
 assert {e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e}==expected
 assert not any(e.get('Action') in ['fail','skip'] for e in events)
assert len(report['runs'])==12
assert [(r['project'],r['mode']) for r in report['runs']]==[(w,m) for w in ['typeorm','trpc','vscode','sentry'] for m in ['baseline','disabled','enabled']]
summary={}
for run in report['runs']:
 assert run['exitStatus']==0
 work=P/run['project']
 for stream in ['stdout','stderr']:
  path=work/(run['mode']+'.'+stream);assert path.read_bytes()==b'' and sha(path)==run[stream+'Sha256']
 ref=R/run['reference'];assert sha(ref)==run['referenceSha256']
 project=next(x for x in json.loads(ref.read_text())['projects'] if x['name']==run['project'])
 assert run['command'][1:]==project['args'] and run['cwd']==project['cwd']
 assert run['inputCount']==len(project['preflight']['candidate']['inputs'])
 assert sha(Path(project['cwd'])/project['args'][1])==project['configSha256']
 for f in project['preflight']['candidate']['inputs']:assert sha(Path(project['cwd'])/f['file'])==f['sha256']
 if run['mode']=='enabled':
  file=work/'census.json';assert run['artifacts']=={'census.json':{'sha256':sha(file),'bytes':file.stat().st_size}}
  data=json.loads(file.read_text());assert data['SchemaVersion']==1 and data['Origins']==['binder','checker'] and data['Stride']==64 and data['Limit']==262144
  groups={}
  for name,g in zip(data['Origins'],data['Groups'],strict=True):
   assert g['Eligible']==(g['Constructed']+63)//64
   assert g['Sampled']==min(g['Eligible'],data['Limit']) and g['Overflow']==g['Eligible']-g['Sampled']
   assert len(g['LiveMasks'])==8 and all(isinstance(v,int) and v>=0 for v in g['LiveMasks'])
   live=sum(g['LiveMasks']);assert live+g['Cleared']==g['Sampled']
   occupied=live-g['LiveMasks'][0]
   groups[name]=dict(g,Live=live,Occupied=occupied,OccupiedFractionAmongLive=occupied/live if live else None)
  summary[run['project']]=groups
 else:assert not run['artifacts']
overlay=json.loads((P/'overlay.json').read_text())['Replace'];assert {k:sha(v) for k,v in overlay.items()}==report['overlaySources']
for rel,origin in [('internal/binder/binder.go',0),('internal/checker/checker.go',1)]:
 source=(P/'staged'/Path(rel).name).read_text();hook=f'\tast.ObserveSymbolColdFields(result, {origin})\n'
 assert source.count(hook)==1 and source.replace(hook,'')==(R/'packages/tsc-go'/rel).read_text()
hook='\n\tif err := ast.WriteSymbolColdFields(program, tr != nil); err != nil {\n\t\tpanic(err)\n\t}\n'
source=(P/'staged/tsc.go').read_text();assert source.count(hook)==1 and source.replace(hook,'')==(R/'packages/tsc-go/internal/execute/tsc.go').read_text()
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
source=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=R,text=True))
assert source['sha256']==report['baseSource'] and source['revision']==report['baseHead']
assert sha(R/'packages/tsc-go/dist/tsc-go')==report['baselineSha256']
assert sha(R/'packages/tsc-go/dist/tsc-go.provenance.json')==report['baselineSidecarSha256']
assert sha('/tmp/tsc-symbol-cold-field-census')==report['candidateSha256']
(P/'summary.json').write_text(json.dumps({'scope':'Observed surviving weak samples only; schedule-dependent systematic sampling, not population or performance estimates.','projects':summary},indent=2)+'\n')
manifest={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f.name not in ['manifest.json'] and '__pycache__' not in f.parts}
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
assert all(sha(P/f)==h for f,h in json.loads((P/'manifest.json').read_text()).items())
print(json.dumps(summary,indent=2))
print('Independent source, control, sample conservation and archive hash verification passed')
