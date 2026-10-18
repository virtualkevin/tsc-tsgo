from pathlib import Path
import json,hashlib,sys
r=Path(__file__).resolve().parents[3];p=Path(__file__).resolve().parent
paths=['packages/tsc-go/internal/checker/types.go','packages/tsc-go/internal/checker/checker.go','packages/tsc-go/internal/checker/pending_members.go','benchmarks/profiles/type-liveness-census/summary.json','benchmarks/profiles/completed-heap-census/analysis.json']
source={x:hashlib.sha256((r/x).read_bytes()).hexdigest() for x in paths}
types=(r/paths[0]).read_text();checker=(r/paths[1]).read_text()
assert 'type TypeBase struct {\n\tType\n}' in types
assert 't := data.AsType()' in checker and 't.data = data' in checker
assert 'd.signatures = append(d.signatures, constructSignatures...)' in checker
assert 'return resolved.signatures[:resolved.callSignatureCount]' in checker
assert 'return t.properties' in types
census=json.loads((r/paths[3]).read_text());heap=json.loads((r/paths[4]).read_text())
rows=[]
for x in census['projects']:
 n=x['totals']['Created']; h=next(z for z in heap['projects'] if z['project']==x['project'])
 rows.append({'project':x['project'],'historicalDiagnosticTypeConstructions':n,'hypothetical24BytesPerEveryConstructedTypeMiB':n*24/1048576,'separateCompletedHeapSampleInuseMiB':h['after']['total']['inuseBytes']/1048576})
result={'scope':'Source-only feasibility/scale audit. Historical diagnostic constructions include non-structured and transient types. 24-byte arithmetic is hypothetical nominal header storage, not an allocator/retained-byte upper bound or performance prediction. Heap values come from a separate diagnostic run; do not interpret ratios as measured savings.','sourceSha256':source,'headerPayloadAlreadyOneAllocation':True,'requiresSliceCapacityAndAliasingAudit':True,'rows':rows,'decision':'No implementation: coallocation premise already satisfied; compact slice representation lacks a demonstrated broad benefit and would require capacity/alias/overflow/reachability validation.'}
text=json.dumps(result,indent=2)+'\n'
if '--write' in sys.argv:(p/'report.json').write_text(text)
else:assert (p/'report.json').read_text()==text
print(json.dumps(rows,indent=2))
