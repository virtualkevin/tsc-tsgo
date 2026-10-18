from pathlib import Path
import hashlib,json,re,statistics,math
p=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'validation.json').read_text());assert v['status']=='passed'
assert v['sources']=={k:sha(f) for k,f in json.loads((p/'overlay.json').read_text())['Replace'].items()}
expected={'TestMapperPlanPureDifferential','TestMapperPlanStatefulHistory','TestMapperPlanFallbackBeforeEffects','TestMapperPlanTypedLifetime','TestMapperPlanNestedHistoriesAndPanics'}
assert [x['name'] for x in v['results']]==['normal','race','checkptr']
for run in v['results']:
 events=[json.loads(line) for line in (p/(run['name']+'.stdout')).read_text().splitlines()]
 assert run['exitCode']==0 and set(run['passed'])==expected
 assert {x['Test'] for x in events if x.get('Action')=='pass' and 'Test' in x}==expected
 assert not any(x.get('Action') in ('fail','skip') for x in events)
b=json.loads((p/'benchmark.json').read_text());assert b['exitCode']==0 and b['sources']==v['sources']
raw=(p/'benchmark.stdout').read_text()
rows=re.findall(r'BenchmarkMapperPlanCosts/(1|2|4|8|32)/(recursive|plan|compile)-\d+\s+\d+\s+([\d.]+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op',raw)
assert len(rows)==75,len(rows)
summary=[]
for n in [1,2,4,8,32]:
 medians={}
 for kind in ['recursive','plan','compile']:
  values=[(float(ns),int(size),int(allocs)) for leaves,k,ns,size,allocs in rows if int(leaves)==n and k==kind];assert len(values)==5
  medians[kind]={'ns':statistics.median(x[0] for x in values),'bytesAllocated':statistics.median(x[1] for x in values),'allocations':statistics.median(x[2] for x in values)}
 delta=medians['recursive']['ns']-medians['plan']['ns']
 summary.append({'leaves':n,'medians':medians,'idealizedAmortizationQueries':math.ceil(medians['compile']['ns']/delta) if delta>0 else None})
result={'status':'passed','focusedTestsPerMode':5,'cases':summary,'scope':'Synthetic fixed-order costs. Idealized amortization divides compile time by evaluation savings; excludes lookup, graph construction, GC and retained-memory cost. Not workload speedup.','rawBenchmarkSha256':sha(p/'benchmark.stdout')}
print(json.dumps(result,indent=2))
