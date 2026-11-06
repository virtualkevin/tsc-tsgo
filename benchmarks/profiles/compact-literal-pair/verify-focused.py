from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
expected={'TestCompactLiteralPairStateAndCopies','TestCompactLiteralPairInterningAndGC','TestCompactLiteralPairLayout'}
report={'passed':False,'runs':[]}
for prefix,size in [('',80),('baseline-',88)]:
 v=json.loads((p/(prefix+'validation.json')).read_text());assert v['status']=='passed'
 overlay=json.loads((p/(prefix+'overlay.json')).read_text())['Replace']
 assert v['sources']=={k:sha(f) for k,f in overlay.items()}
 assert [r['name'] for r in v['results']]==['normal','race','checkptr']
 for r in v['results']:
  stdout=p/(prefix+r['name']+'.stdout');stderr=p/(prefix+r['name']+'.stderr')
  events=[json.loads(l) for l in stdout.read_text().splitlines()]
  passed=[e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e]
  assert r['exitCode']==0 and len(passed)==3 and set(passed)==set(r['passed'])==expected
  assert not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
  assert any(f'Type=56 LiteralType={size}' in e.get('Output','') for e in events)
  flags={'normal':[],'race':['-race'],'checkptr':['-gcflags=all=-d=checkptr=2']}[r['name']]
  assert r['command']==['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1','-overlay',str(p/(prefix+'overlay.json')),*flags,'./internal/checker','-run','^TestCompactLiteralPair']
  report['runs'].append({'representation':prefix or 'candidate','mode':r['name'],'stdoutSha256':sha(stdout),'stderrSha256':sha(stderr),'tests':passed})
report.update(passed=True,verifierSha256=sha(__file__))
(p/'focused-readback.json').write_text(json.dumps(report,indent=2)+'\n')
print('18 focused raw test outcomes and both layouts verified')
