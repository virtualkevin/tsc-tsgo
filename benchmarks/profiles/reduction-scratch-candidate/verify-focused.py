from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
r=json.loads((p/'validation.json').read_text());assert r['status']=='passed'
assert r['controllerSha256']==sha(p/'validate.py')
assert r['sources']=={str(f):sha(f) for f in (p/'staged').glob('*.go')}
required={'TestScratchReductionMatchesOriginalGrouping','TestScratchSharedSymbolDoesNotResolveType','TestScratchRecursiveOwnershipAndCleanup','TestScratchCleanupOnPanic','TestValueSymbolLinksRetainInstantiatedGraphAcrossGC','TestValueSymbolLinksReplacementKeepsPublishedPointers'}
assert [x['name'] for x in r['results']]==['normal','race','checkptr'];sets=[];counts=[]
for run in r['results']:
 name=run['name'];stdout=p/(name+'.stdout');stderr=p/(name+'.stderr')
 assert sha(stdout)==run['stdoutSha256'] and sha(stderr)==run['stderrSha256'] and run['exitCode']==0 and run['ok']
 events=[json.loads(x) for x in stdout.read_text().splitlines()]
 assert not any(x.get('Action') in ['fail','skip','build-fail'] for x in events)
 tests=[x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x]
 assert tests==run['passed'] and required.issubset(tests)
 assert len([t for t in tests if t.startswith('TestScratchReductionMatchesOriginalGrouping/')])==64
 assert [x['Package'] for x in events if x.get('Action')=='pass' and 'Test' not in x]==['github.com/microsoft/typescript-go/internal/checker']
 assert ('-race' in run['command'])==(name=='race')
 flags=[x for x in run['command'] if x.startswith('-gcflags=')]
 assert flags==(['-gcflags=all=-d=checkptr=2','-gcflags=github.com/microsoft/typescript-go/...=-l=4 -d=checkptr=2'] if name=='checkptr' else ['-gcflags=github.com/microsoft/typescript-go/...=-l=4'])
 sets.append(set(tests));counts.append(len(tests))
assert sets[0]==sets[1]==sets[2]
(p/'focused-readback.json').write_text(json.dumps({'passed':True,'validationSha256':sha(p/'validation.json'),'counts':counts,'scope':'Raw event identities/counts/packages, source/log/controller hashes and exact mode-specific build flags.'},indent=2)+'\n')
print('Independently verified focused records:',counts)
