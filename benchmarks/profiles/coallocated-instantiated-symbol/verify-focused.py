from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
r=json.loads((p/'validation.json').read_text());assert r['status']=='passed'
assert r['controllerSha256']==sha(p/'validate.py')
assert r['sources']=={str(f):sha(f) for f in (p/'staged').glob('*.go')}
expected={'TestPointerLinkStoreInstallHistory','TestPointerLinkStoreDifferential','TestPointerLinkStoreNilAndReplacement','TestPointerLinkStoreCollisionsAndGrowth','TestPointerLinkStoreRetainsDisplacedArenaSlots','TestPointerLinkStoreConcurrentReadOnlyCopies','TestInstantiatedSymbolCoallocationIdentity','TestValueSymbolLinksRetainInstantiatedGraphAcrossGC','TestValueSymbolLinksReplacementKeepsPublishedPointers'}
assert [x['name'] for x in r['results']]==['normal','race','checkptr']
for run in r['results']:
 name=run['name'];stdout=p/(name+'.stdout');stderr=p/(name+'.stderr');assert sha(stdout)==run['stdoutSha256'] and sha(stderr)==run['stderrSha256'];assert run['exitCode']==0 and run['ok']
 events=[json.loads(l) for l in stdout.read_text().splitlines()];assert not any(x.get('Action') in ('fail','skip','build-fail') for x in events)
 tests=[x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x];assert len(tests)==9 and set(tests)==expected and tests==run['passed']
 packages=[x['Package'] for x in events if x.get('Action')=='pass' and 'Test' not in x];assert set(packages)=={'github.com/microsoft/typescript-go/internal/core','github.com/microsoft/typescript-go/internal/checker'} and len(packages)==2
 assert ('-race' in run['command'])==(name=='race');assert ('-gcflags=all=-d=checkptr=2' in run['command'])==(name=='checkptr')
baseline=json.loads((p/'baseline-validation.json').read_text());assert baseline['status']=='passed'
assert baseline['controllerSha256']==sha(p/'validate-baseline.py')
assert baseline['sources']=={v:sha(Path(v)) for v in json.loads((p/'baseline-overlay.json').read_text())['Replace'].values()}
assert [x['name'] for x in baseline['results']]==['normal','race','checkptr']
for run in baseline['results']:
 name=run['name'];stdout=p/('baseline-'+name+'.stdout');stderr=p/('baseline-'+name+'.stderr')
 assert sha(stdout)==run['stdoutSha256'] and sha(stderr)==run['stderrSha256'] and run['exitCode']==0 and run['ok']
 events=[json.loads(l) for l in stdout.read_text().splitlines()];assert not any(x.get('Action') in ('fail','skip','build-fail') for x in events)
 tests=[x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x];assert len(tests)==8 and set(tests)==expected-{'TestPointerLinkStoreInstallHistory'} and tests==run['passed']
 packages=[x['Package'] for x in events if x.get('Action')=='pass' and 'Test' not in x];assert set(packages)=={'github.com/microsoft/typescript-go/internal/core','github.com/microsoft/typescript-go/internal/checker'} and len(packages)==2
 assert ('-race' in run['command'])==(name=='race');assert ('-gcflags=all=-d=checkptr=2' in run['command'])==(name=='checkptr')
candidateTest=(p/'staged/instantiated_symbol_record_test.go').read_text();baselineTest=(p/'baseline-staged/instantiated_symbol_record_test.go').read_text()
assert candidateTest.replace('t.Logf("layout symbol=%d links=%d record=%d", unsafe.Sizeof(ast.Symbol{}), unsafe.Sizeof(ValueSymbolLinks{}), unsafe.Sizeof(instantiatedSymbolRecord{}))','t.Logf("layout symbol=%d links=%d", unsafe.Sizeof(ast.Symbol{}), unsafe.Sizeof(ValueSymbolLinks{}))')==baselineTest
(p/'focused-readback.json').write_text(json.dumps({'passed':True,'validationSha256':sha(p/'validation.json'),'baselineValidationSha256':sha(p/'baseline-validation.json'),'testRecords':51,'scope':'Raw test events, exact nine candidate/eight retained tests per mode, flags, hashes, package completion, unchanged source. Same constructor history differs only in layout logging. Does not establish full compiler parity or performance.'},indent=2)+'\n')
print('All51 focused test records independently verified')
