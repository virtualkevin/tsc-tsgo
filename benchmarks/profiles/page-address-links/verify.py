from pathlib import Path
import hashlib,json,re,statistics
p=Path(__file__).resolve().parent
v=json.loads((p/'validation.json').read_text())
for name,digest in v['sources'].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
expected={'TestPageAddressLinksDifferential','TestPageAddressLinksUnlinkedLifetime','TestPageAddressLinksLinkedLifetime','TestPageAddressLinksConcurrentReads','TestPageAddressLinksRegionBoundaries'}
assert len(v['tests'])==3
for test in v['tests']:
 records=[json.loads(x) for x in (p/(test['name']+'.jsonl')).read_text().splitlines()]
 passed={x['Test'] for x in records if x.get('Action')=='pass' and 'Test' in x}
 assert passed==expected and set(test['passed'])==expected and test['code']==0
 assert not any(x.get('Action') in ('fail','skip') for x in records)
 assert any(x.get('Action')=='pass' and 'Test' not in x for x in records)
text=(p/'lookup.stdout').read_text()
assert '\nPASS\n' in text and v['microbenchmark']['code']==0
samples={}
for size,kind,ns in re.findall(r'BenchmarkPageAddressLinksLookup/(\d+)/(pointer|page)-\d+\s+\d+\s+([\d.]+) ns/op\s+0 B/op\s+0 allocs/op',text):
 samples.setdefault((int(size),kind),[]).append(float(ns))
assert set(samples)=={(size,kind) for size in (256,65536) for kind in ('pointer','page')}
assert all(len(x)==5 for x in samples.values())
result={'kind':'isolated lookup mechanism; not compiler performance','observations':[
 {'keys':size,'pointerMedianNs':statistics.median(samples[size,'pointer']),'pageMedianNs':statistics.median(samples[size,'page'])} for size in (256,65536)],
 'decision':'Decline compiler integration: no measured lookup advantage. Non-alternating microbenchmark is not a workload acceptance test.'}
encoded=json.dumps(result,indent=2)+'\n'
if (p/'summary.json').exists():assert (p/'summary.json').read_text()==encoded
else:(p/'summary.json').write_text(encoded)
print(encoded,end='')
