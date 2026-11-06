"""Machine-check the bitvector model, not the Go implementation or compiler."""
from pathlib import Path
import hashlib,json
import z3 as z
p=Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert z.get_version_string()=='4.15.4'
v=json.loads((p/'validation.json').read_text());assert v['passed']
assert v['sources']=={f.name:sha(f) for f in (p/'prototype').iterdir() if f.is_file()}
claims=[]
def prove(name,bad,*assumptions):
 s=z.Solver();s.add(*assumptions,bad)
 result=s.check();assert result==z.unsat,(name,result,s.model() if result==z.sat else '')
 claims.append({'claim':name,'counterexampleQuery':'unsat'})
def split(k):
 source=z.LShR(k,32);target=z.LShR(k,2)&((1<<30)-1)
 index=((source&15)<<4)|(target&15)
 return k & ~z.BitVecVal((15<<32)|(15<<2),64),index,z.And(source!=0,z.ULT(source,1<<30),target!=0)
x,y=z.BitVecs('x y',64);tx,ix,ex=split(x);ty,iy,ey=split(y)
rebuilt=tx | (z.LShR(ix,4)<<32) | ((ix&15)<<2)
prove('tile plus lane reconstructs every 64-bit key',rebuilt!=x)
prove('distinct keys cannot share tile and lane',z.And(x!=y,tx==ty,ix==iy))
prove('eligible keys exclude fallback and reserved high bits',z.And(ex,(x & z.BitVecVal(3<<62,64))!=0))
prove('intersection state retained in tile',tx&3 != x&3)
prove('lane is inside 256-bit tile',z.UGE(ix,256))
wordx=z.LShR(ix,6);wordy=z.LShR(iy,6)
maskx=z.BitVecVal(1,64)<<(ix&63);masky=z.BitVecVal(1,64)<<(iy&63)
prove('distinct lanes have distinct word/mask addresses',z.And(ix!=iy,wordx==wordy,maskx==masky))
# One-key abstract Set transition. Other keys are disjoint by the claims above.
tile,other,eligible=z.Bools('tile other eligible')
value=z.BitVec('value',32)
oldSize=z.If(tile,1,0)+z.If(other,1,0)
nextTile=z.And(eligible,value==2)
nextOther=z.Not(nextTile)
nextSize=z.If(nextTile,1,0)+z.If(nextOther,1,0)
nextGet=z.If(nextTile,z.BitVecVal(2,32),value)
invariant=z.And(z.Not(z.And(tile,other)),z.Implies(tile,eligible))
prove('Set has exclusive representation',z.And(nextTile,nextOther),invariant)
prove('Set reads back every full-width result',nextGet!=value,invariant)
prove('Set increments logical size iff key was absent',nextSize!=oldSize+z.If(z.Or(tile,other),0,1),invariant)
report={'passed':True,'solver':'z3-solver 4.15.4.0','claims':claims,'sources':v['sources'],'proofScriptSha256':sha(__file__),'scope':'Machine-checked bitvector/one-key transition model. Translation to Go, Go map/array behavior, memory safety, concurrency, compiler key equivalence, semantic integration, and performance are not proved. Go differential histories independently test the supplied implementation.'}
(p/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
