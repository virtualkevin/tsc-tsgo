from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;r=p.parents[2];src=r/'packages/tsc-go/internal/checker/checker.go';before=src.read_text();after=(p/'staged/checker.go').read_text()
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(src)==json.loads((p/'source.json').read_text())['baseSha256']
start=before.index('func instantiateList[');end=before.index('\nfunc ',start+1);generic=before[start:end]
body=generic[generic.index('{\n')+2:]
expected=before
for name,arg,typ,single in [('Types','types','Type','Type'),('Symbols','symbols','ast.Symbol','Symbol'),('Signatures','signatures','Signature','Signature'),('IndexInfos','indexInfos','IndexInfo','IndexInfo')]:
 old=f'func (c *Checker) instantiate{name}({arg} []*{typ}, m *TypeMapper) []*{typ} {{\n\treturn instantiateList(c, {arg}, m, (*Checker).instantiate{single})\n}}'
 direct=body.replace('values',arg).replace('[]T','[]*'+typ).replace('instantiator(c, value, m)',f'c.instantiate{single}(value, m)').replace(f'instantiator(c, {arg}[j], m)',f'c.instantiate{single}({arg}[j], m)')
 new=f'func (c *Checker) instantiate{name}({arg} []*{typ}, m *TypeMapper) []*{typ} {{\n'+direct.rstrip('\n')
 assert expected.count(old)==1
 expected=expected.replace(old,new)
assert after==expected,'candidate differs from four mechanical loop specializations'
print(json.dumps({'passed':True,'baseSha256':sha(src),'candidateSha256':sha(p/'staged/checker.go'),'auditSha256':sha(__file__),'scope':'Exact source specialization of unchanged generic body at all four callers; not a compiled-code or whole-compiler proof.'},indent=2))
