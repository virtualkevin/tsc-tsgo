"""Bit-vector packing lemmas only, not Go/GC/whole-graph implementation proofs."""
from pathlib import Path
import hashlib,json,re
import z3
p=Path(__file__).resolve().parent;source=p/'prototype/graph.go';s=source.read_text()
assert re.search(r'const pageBits = 8\b',s)
for expression in ['index := uint32(h) - 1','g.pages[index>>pageBits][index&pageMask]','if g.count == g.limit {','g.count++','h := handle(g.count)']:
 assert expression in s,expression
bits=int(re.search(r'const pageBits = (\d+)',s)[1]);mask=(1<<bits)-1
h,k,count,limit=z3.BitVecs('h k count limit',32)
def page(x):return z3.LShR(x-1,bits)
def slot(x):return (x-1)&mask
claims={
 'decode_reencode':z3.Implies(h!=0,((page(h)<<bits)|slot(h))+1==h),
 'slot_bound':z3.Implies(h!=0,z3.ULT(slot(h),1<<bits)),
 'page_bound':z3.Implies(h!=0,z3.ULE(page(h),0xffffffff>>bits)),
 'scoped_injectivity':z3.Implies(z3.And(h!=0,k!=0,page(h)==page(k),slot(h)==slot(k)),h==k),
 'allocation_no_wrap':z3.Implies(z3.ULT(count,limit),z3.And(count+1!=0,z3.UGT(count+1,count),z3.ULE(count+1,limit))),
 'last_handle_location':z3.Implies(h==0xffffffff,z3.And(page(h)==0xffffff,slot(h)==254)),
}
results=[]
for name,claim in claims.items():
 solver=z3.Solver();solver.add(z3.Not(claim));answer=solver.check();assert answer==z3.unsat,(name,answer)
 results.append({'name':name,'counterexampleQuery':str(answer)})
solver=z3.Solver();solver.add(h!=0,k!=0,h!=k,page(h)==page(k),((h-1)&(mask>>1))==((k-1)&(mask>>1)))
assert solver.check()==z3.sat
m=solver.model();witness={str(x):m[x].as_long() for x in [h,k]}
assert witness['h']!=witness['k'] and ((witness['h']-1)>>bits)==((witness['k']-1)>>bits) and ((witness['h']-1)&(mask>>1))==((witness['k']-1)&(mask>>1))
report={'scope':'Unsigned 32-bit handle arithmetic within one owner. Parameter/expression text checks link this model to recorded source, but do not prove Go execution, Graph invariants, GC retention, concurrent safety, compiler compatibility or performance. Allocation lemma assumes count<limit; callers maintain count<=limit.','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controllerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'solver':z3.get_full_version(),'pageBits':bits,'claims':results,'negativeControl':{'description':'Halving the slot mask loses a bit and aliases distinct handles within a page.','result':'sat','witness':witness}}
(p/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
print('Six arithmetic claims unsat; broken-mask control sat:',witness)
