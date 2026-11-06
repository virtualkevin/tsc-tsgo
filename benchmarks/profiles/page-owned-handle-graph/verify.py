from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
expected={'TestStatefulGraphAgreement','TestOwnershipAndFailureAtomicity','TestRemoteCapacityAndReuse','TestPageGraphReachability','TestEscapedRootAndConcurrentReads','TestRecordLayout','TestUnreachableRemoteCycleCollected'}
r=json.loads((p/'validation.json').read_text());assert r['status']=='passed' and r['controllerSha256']==sha(p/'validate.py');assert r['sources']=={str(f):sha(f) for f in (p/'prototype').glob('*')}
assert [x['mode'] for x in r['runs']]==['normal','race','checkptr']
for run in r['runs']:
 mode=run['mode'];assert run['exitCode']==0 and run['ok'];assert ('-race' in run['command'])==(mode=='race');assert ('-gcflags=all=-d=checkptr=2' in run['command'])==(mode=='checkptr')
 for stream in ['stdout','stderr']:assert sha(p/(mode+'.'+stream))==run[stream+'Sha256']
 events=[json.loads(l) for l in (p/(mode+'.stdout')).read_text().splitlines()];assert not any(x.get('Action') in ('fail','skip','build-fail') for x in events)
 tests=[x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x];assert len(tests)==7 and set(tests)==expected and tests==run['passed']
 assert len([x for x in events if x.get('Action')=='pass' and 'Test' not in x])==1
for name in ['failed-initial-build','six-test-checkpoint']:
 d=p/name
 for f,h in json.loads((d/'manifest.json').read_text()).items():assert sha(d/f)==h
 prior=json.loads((d/'validation.json').read_text())
 for f,h in prior['sources'].items():assert sha(d/'prototype'/Path(f).name)==h
 if name=='failed-initial-build':assert prior['status']=='failed' and prior['runs'][0]['exitCode']!=0
 else:
  assert prior['status']=='passed' and len(prior['runs'])==3 and all(x['exitCode']==0 and len(x['passed'])==6 for x in prior['runs'])
  assert sha(d/'prototype/graph.go')==sha(p/'prototype/graph.go')
(p/'readback.json').write_text(json.dumps({'passed':True,'testRecords':21,'validationSha256':sha(p/'validation.json'),'verifierSha256':sha(Path(__file__)),'sources':r['sources'],'scope':'Exact normal/race/checkptr test identities and raw events, source hashes, previous failed compile and successful six-test checkpoint hashes. Finite standalone tests, not compiler correctness, performance or a whole-program proof.'},indent=2)+'\n')
print('Verified21 final test records and preserved earlier checkpoints')
