from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
r=json.loads((p/'validation.json').read_text());assert r['status']=='passed'
sources={f.name:sha(f) for f in (p/'prototype').iterdir() if f.suffix=='.go' or f.name=='go.mod'}
assert sources==r['sources'] and r['controllerSha256']==sha(p/'validate.py')
expected={'TestStatefulGraphAgainstIndependentModel','TestOwnerAndExhaustionFailuresAreAtomic','TestPublishedRefRetainsPagesAcrossGCAndGrowth','TestConcurrentCompletedReads','TestLayoutAndHandleBoundaries'}
assert [x['mode'] for x in r['runs']]==['normal','race','checkptr']
layouts=[]
for run in r['runs']:
 mode=run['mode'];flags={'normal':[],'race':['-race'],'checkptr':['-gcflags=all=-d=checkptr=2']}[mode]
 assert run['command']==['/tmp/tsc-toolchains/go/bin/go','test','-json','-count=1',*flags,'./...']
 assert run['exitCode']==0 and run['ok'] and set(run['passed'])==expected
 for stream in ['stdout','stderr']:assert sha(p/(mode+'.'+stream))==run[stream+'Sha256']
 events=[json.loads(x) for x in (p/(mode+'.stdout')).read_text().splitlines()]
 assert {e['Test'] for e in events if e.get('Action')=='pass' and 'Test' in e}==expected
 assert not any(e.get('Action') in ['fail','skip','build-fail'] for e in events)
 text=''.join(e.get('Output','') for e in events)
 matches=re.findall(r'record=(\d+) page=(\d+) publishedRef=(\d+) graph=(\d+)',text)
 assert matches==[('32','8192','16','32')];layouts.append(matches[0])
proof=json.loads((p/'proof.json').read_text());assert proof['sourceSha256']==sources['graph.go'] and proof['controllerSha256']==sha(p/'prove.py')
assert len(proof['claims'])==6 and all(x['counterexampleQuery']=='unsat' for x in proof['claims']) and proof['negativeControl']['result']=='sat'
go='/tmp/tsc-toolchains/go/bin/go';version=subprocess.check_output([go,'version'],text=True).strip();assert version=='go version go1.26.9 linux/amd64'
(p/'readback.json').write_text(json.dumps({'passed':True,'scope':'Independent source and raw test event/hash readback; arithmetic report verified for source binding and stated solver outcomes, not an independent prover or whole implementation proof.','sources':sources,'toolchain':{'path':go,'sha256':sha(go),'version':version},'layouts':layouts,'evidence':{n:sha(p/n) for n in ['validation.json','proof.json','normal.stdout','normal.stderr','race.stdout','race.stderr','checkptr.stdout','checkptr.stderr']},'verifierSha256':sha(__file__)},indent=2)+'\n')
print('15 raw test outcomes, measured layouts, source/proof pins verified')
