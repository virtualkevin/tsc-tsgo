from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;m=p.parents[2]/'packages/tsc-go';paths={};base={}
for name in ['types.go','checker.go','relater.go']:
 src=m/'internal/checker'/name;s=src.read_text();base[str(src)]=hashlib.sha256(src.read_bytes()).hexdigest()
 if name=='types.go':
  s=s.replace('id          TypeId\n','id          TypeId\n literalState uint8 // Private LiteralType state, stored in existing header padding.\n',1)
  s=s.replace('freshType   *Type // Fresh version of type\n\tregularType *Type // Regular version of type','literalPartner *Type // Other freshness form; role and initialization are in Type.literalState.')
  s=s.replace('return t.freshType','''if t.literalState&2 != 0 {
   if t.literalState&4 == 0 {return nil}
   return t.data.AsType()
  }
  return t.literalPartner''',1)
  s=s.replace('return t.regularType','''if t.literalState&1 == 0 {return nil}
  if t.literalState&2 != 0 {return t.literalPartner}
  return t.data.AsType()''',1)
 else:
  s=re.sub(r'([\w.()]+\.AsLiteralType\(\))\.freshType = ([^\n]+)',r'\1.setFreshType(\2)',s)
  s=s.replace('d.freshType = f','d.setFreshType(f)')
  s=s.replace('data.regularType = regularType','data.literalState = 3\n data.literalPartner = regularType').replace('data.regularType = t','data.literalState = 1')
  s=s.replace('.AsLiteralType().regularType','.AsLiteralType().RegularType()').replace('.AsLiteralType().freshType','.AsLiteralType().FreshType()')
  s=s.replace('d.freshType','d.FreshType()').replace('literal.regularType','literal.RegularType()').replace('literal.freshType','literal.FreshType()')
 dest=p/'staged'/name;dest.write_text(s);paths[str(src)]=str(dest)
for name in ['compact_literal_pair.go','compact_literal_pair_test.go']:
 paths[str(m/'internal/checker'/name)]=str(p/'staged'/name)
for file in paths.values():subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',file],check=True)
(p/'base.json').write_text(json.dumps(base,indent=2)+'\n');(p/'overlay.json').write_text(json.dumps({'Replace':paths},indent=2)+'\n')
