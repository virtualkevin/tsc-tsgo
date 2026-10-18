from pathlib import Path
import hashlib,json,subprocess
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
r=load(out/'report.json');assert r['status']=='passed' and len(r['runs'])==12
assert r['controllerSha256']==sha(out/'capture.py') and r['validationSha256']==sha(out/'validation.json')
v=load(out/'validation.json');b=load(out/'build.json');overlay=load(out/'overlay.json')['Replace']
assert v['passed'] and b['exitCode']==0 and len(v['runs'])==2
assert v['overlaySources']==b['overlaySources']=={k:sha(p) for k,p in overlay.items()}
assert r['overlaySources']=={str(Path(k).relative_to(root)):sha(p) for k,p in overlay.items()}
for run in v['runs']:
 assert run['passed'] and run['exitCode']==0 and len(run['tests'])==3
 assert all(action=='pass' for _,action in run['tests'])
 assert sha(out/(run['mode']+'.jsonl'))==run['stdoutSha256']
 assert sha(out/(run['mode']+'.stderr'))==run['stderrSha256']
assert sha('/tmp/tsc-declaration-path-census')==b['binarySha256']==r['candidateSha256']
assert sha(root/'packages/tsc-go/dist/tsc-go')==r['baselineSha256']=='8fe4bd800cdb24434745e4ad87a8376e0f689b8f12d63a2fbcd0293a7d200b4f'
seen=set();summaries=[]
for run in r['runs']:
 project,mode=run['project'],run['mode'];assert (project,mode) not in seen;seen.add((project,mode))
 assert run['exitStatus']==0;work=out/project
 for stream in ['stdout','stderr']:
  f=work/(mode+'.'+stream);assert sha(f)==run[stream+'Sha256'] and f.read_bytes()==b''
 group='small' if project in ['typeorm','trpc'] else 'large';ref=root/f'benchmarks/results/native-node-pointer/{group}.json'
 assert sha(ref)==run['referenceSha256'];p=next(p for p in load(ref)['projects'] if p['name']==project)
 assert run['cwd']==p['cwd'] and run['command'][1:]==p['args']
 expected=root/'packages/tsc-go/dist/tsc-go' if mode=='baseline' else Path('/tmp/tsc-declaration-path-census')
 assert run['command'][0]==str(expected)
 assert sha(Path(p['cwd'])/p['args'][1])==p['configSha256']
 inputs=p['preflight']['candidate']['inputs'];assert run['inputCount']==len(inputs)
 for f in inputs:assert sha(Path(p['cwd'])/f['file'])==f['sha256']
 if mode!='enabled':assert run['counts'] is None and run['censusSha256'] is None;continue
 assert sha(work/'census.json')==run['censusSha256'];c=load(work/'census.json');rows=c['Rows'];assert c['Schema']==1 and rows==run['counts']
 assert rows==sorted(rows,key=lambda x:(x['Explicit'],x['Emitter']))
 assert len({(x['Explicit'],x['Emitter']) for x in rows})==len(rows)
 for row in rows:
  assert set(row)=={'Explicit','Emitter','Files'} and all(type(x)==int and x>=0 for x in row.values())
  assert row['Files']>0 and row['Explicit']+row['Emitter']>0
 summaries.append({'project':project,'sourceIdentities':sum(x['Files'] for x in rows),'explicitTransforms':sum(x['Explicit']*x['Files'] for x in rows),'emitterTransforms':sum(x['Emitter']*x['Files'] for x in rows),'overlapIdentities':sum(x['Files'] for x in rows if x['Explicit'] and x['Emitter']),'repeatedIdentities':sum(x['Files'] for x in rows if max(x['Explicit'],x['Emitter'])>1)})
assert seen=={(p,m) for p in ['typeorm','trpc','vscode','sentry'] for m in ['baseline','disabled','enabled']}
js='import {captureGoSources} from "./scripts/build-provenance.mjs";console.log(JSON.stringify(captureGoSources(process.cwd()+"/packages/tsc-go")))'
current=json.loads(subprocess.check_output(['node','--input-type=module','-e',js],cwd=root,text=True));assert current['sha256']==r['baseSource'] and current['revision']==r['baseHead']
result={'passed':True,'reportSha256':sha(out/'report.json'),'summaries':summaries,'limitation':'Diagnostic observer retains source graphs; these are event counts, not timing or removable work.'}
(out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
