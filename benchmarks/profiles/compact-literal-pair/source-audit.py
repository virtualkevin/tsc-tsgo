from pathlib import Path
import hashlib,json,re,subprocess
p=Path(__file__).resolve().parent;m=p.parents[2]/'packages/tsc-go'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fmt=lambda s:subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=s.encode()).decode()
base=json.loads((p/'base.json').read_text());assert all(sha(k)==v for k,v in base.items())
s=(p/'staged/checker.go').read_text()
s=re.sub(r'([\w.()]+\.AsLiteralType\(\))\.setFreshType\(([^\n]+)\)',r'\1.freshType = \2',s)
s=s.replace('d.setFreshType(f)','d.freshType = f')
s=s.replace('data.literalState = 3\n\t\tdata.literalPartner = regularType','data.regularType = regularType').replace('data.literalState = 1','data.regularType = t')
s=s.replace('.AsLiteralType().RegularType()','.AsLiteralType().regularType').replace('.AsLiteralType().FreshType()','.AsLiteralType().freshType').replace('d.FreshType()','d.freshType')
assert fmt(s)==(m/'internal/checker/checker.go').read_text()
s=(p/'staged/relater.go').read_text().replace('.AsLiteralType().RegularType()','.AsLiteralType().regularType').replace('literal.RegularType()','literal.regularType').replace('literal.FreshType()','literal.freshType')
assert fmt(s)==(m/'internal/checker/relater.go').read_text()
s=(p/'staged/types.go').read_text()
s=re.sub(r'^\s*literalState uint8[^\n]*\n','',s,flags=re.M)
s=s.replace('literalPartner *Type // Other freshness form; role and initialization are in Type.literalState.','freshType *Type // Fresh version of type\n regularType *Type // Regular version of type')
a=s.index('func (t *LiteralType) FreshType()');b=s.index('func (t *LiteralType) String()',a)
assert s[a:b]=='''func (t *LiteralType) FreshType() *Type {
	if t.literalState&2 != 0 {
		if t.literalState&4 == 0 {
			return nil
		}
		return t.data.AsType()
	}
	return t.literalPartner
}

func (t *LiteralType) RegularType() *Type {
	if t.literalState&1 == 0 {
		return nil
	}
	if t.literalState&2 != 0 {
		return t.literalPartner
	}
	return t.data.AsType()
}

'''
s=s[:a]+'''func (t *LiteralType) FreshType() *Type {
 return t.freshType
}

func (t *LiteralType) RegularType() *Type {
 return t.regularType
}

'''+s[b:]
assert fmt(s)==(m/'internal/checker/types.go').read_text()
paths=json.loads((p/'overlay.json').read_text())['Replace'];assert len(paths)==5
(p/'source-audit.json').write_text(json.dumps({'passed':True,'sources':{k:sha(v) for k,v in paths.items()},'base':base,'controllerSha256':sha(__file__),'scope':'Three modified production files restore exactly after reversing the specified layout, accessor and write-site substitutions; helper and tests separately reviewed. Not a full correctness proof.'},indent=2)+'\n')
print('Scoped source inverse verified')
