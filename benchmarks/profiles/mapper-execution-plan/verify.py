from pathlib import Path
import hashlib,json,re,statistics
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'validation.json').read_text());assert v['status']=='passed'
assert v['sources']=={k:sha(f) for k,f in json.loads((p/'overlay.json').read_text())['Replace'].items()}
expected={'TestMapperPlanPureDifferential','TestMapperPlanStatefulHistory','TestMapperPlanFallbackBeforeEffects','TestMapperPlanTypedLifetime'}
assert [x['name'] for x in v['results']]==['normal','race','checkptr']
for run in v['results']:
 events=[json.loads(line) for line in (p/(run['name']+'.stdout')).read_text().splitlines()]
 assert run['exitCode']==0 and set(run['passed'])==expected
 assert {x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x}==expected
 assert not any(x.get('Action') in ('fail','skip') for x in events)
b=json.loads((p/'benchmark.json').read_text());assert b['exitCode']==0 and b['sources']==v['sources']
raw=(p/'benchmark.stdout').read_text();rows=re.findall(r'BenchmarkMapperPlanMerged/(recursive|plan)-\d+\s+\d+\s+([\d.]+) ns/op\s+0 B/op\s+0 allocs/op',raw)
medians={}
for name in ['recursive','plan']:
 values=[float(value) for kind,value in rows if kind==name];assert len(values)==5
 medians[name]=statistics.median(values)
result={'status':'passed','focusedTestsPerMode':4,'mechanismMedianNs':medians,'ratioOfMechanismMedians':medians['recursive']/medians['plan'],'scope':'Synthetic fixed-order 32-link chain only; excludes compile and retained memory; not compiler speedup or proof','rawBenchmarkSha256':sha(p/'benchmark.stdout')}
print(json.dumps(result,indent=2))
