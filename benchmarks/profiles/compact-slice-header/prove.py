from pathlib import Path
import hashlib,json
import z3
p=Path(__file__).resolve().parent
n,c=z3.BitVecs('length capacity',64)
max32=z3.BitVecVal(2**32-1,64);sentinel=z3.BitVecVal(2**64-1,64)
valid=z3.And(z3.ULE(n,c),z3.ULE(c,max32),z3.Not(z3.And(n==max32,c==max32)))
shape=(c<<32)|n
n2,c2=z3.BitVecs('length2 capacity2',64)
valid2=z3.And(z3.ULE(n2,c2),z3.ULE(c2,max32),z3.Not(z3.And(n2==max32,c2==max32)))
claims={
 'length_roundtrip':z3.Implies(valid,(shape&max32)==n),
 'capacity_roundtrip':z3.Implies(valid,z3.LShR(shape,32)==c),
 'sentinel_exclusion':z3.Implies(valid,shape!=sentinel),
 'injectivity':z3.Implies(z3.And(valid,valid2,shape==((c2<<32)|n2)),z3.And(n==n2,c==c2)),
 'zero_header_shape':z3.Implies(valid,(shape==0)==z3.And(n==0,c==0)),
}
results={}
for name,claim in claims.items():
 s=z3.Solver();s.add(z3.Not(claim));result=s.check();assert result==z3.unsat,(name,str(result));results[name]=str(result)
# The evidence pipeline must reject a false extraction rule.
s=z3.Solver();s.add(valid,(shape&max32)!=c);assert s.check()==z3.sat
result={'solverVersion':z3.get_version_string(),'claims':results,'negativeControl':'sat','sourceSha256':hashlib.sha256((p/'prototype/slice.go').read_bytes()).hexdigest(),'scope':'64-bit packing model only. Not a proof of Go implementation, pointer safety, GC, compiler equivalence or performance. Source uses the same capacity shift, length OR and all-ones sentinel; source linkage is a review plus hash pin, not verified translation.'}
(p/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
