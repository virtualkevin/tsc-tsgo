from pathlib import Path
import difflib,hashlib,json
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go'
stage=p/'staged';stage.mkdir(exist_ok=True)
replacements={
'internal/checker/checker.go':[
 ('core.LinkStore[*ast.Symbol, SymbolReferenceLinks]','map[*ast.Symbol]ast.SymbolFlags'),
 ('c.symbolReferenceLinks.Get(symbol).referenceKinds |= meaning','if c.symbolReferenceLinks == nil {\n\t\tc.symbolReferenceLinks = make(map[*ast.Symbol]ast.SymbolFlags)\n\t}\n\tc.symbolReferenceLinks[symbol] |= meaning'),
 ('c.symbolReferenceLinks.Get(target).referenceKinds |= ast.SymbolFlagsAll','c.symbolReferenced(target, ast.SymbolFlagsAll)'),
 ('c.symbolReferenceLinks.Get(symbol).referenceKinds','c.symbolReferenceLinks[symbol]'),
 ('c.symbolReferenceLinks.Get(local).referenceKinds','c.symbolReferenceLinks[local]'),
 ('c.symbolReferenceLinks.Get(c.getSymbolOfDeclaration(node)).referenceKinds','c.symbolReferenceLinks[c.getSymbolOfDeclaration(node)]'),
 ('c.symbolReferenceLinks.Get(c.getMergedSymbol(typeParameter.Symbol())).referenceKinds','c.symbolReferenceLinks[c.getMergedSymbol(typeParameter.Symbol())]')],
'internal/checker/types.go':[
 ('// Links for referenced symbols\n\ntype SymbolReferenceLinks struct {\n\treferenceKinds ast.SymbolFlags // Flags for the meanings of the symbol that were referenced\n}\n\n','')]}
overlay={};patch=[];base={}
for name,pairs in replacements.items():
 source=m/name;old=source.read_text();new=old
 base[name]=hashlib.sha256(source.read_bytes()).hexdigest()
 for a,b in pairs:
  assert new.count(a)==(2 if 'Get(c.getSymbolOfDeclaration(node))' in a else 1),(name,a,new.count(a))
  new=new.replace(a,b)
 assert 'SymbolReferenceLinks' not in new
 dest=stage/Path(name).name;dest.write_text(new)
 overlay[str(source)]=str(dest)
 patch+=difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/packages/tsc-go/'+name,tofile='b/packages/tsc-go/'+name)
overlay[str(m/'internal/checker/direct_reference_flags_test.go')]=str(p/'direct_reference_flags_test.go')
(p/'candidate.patch').write_text(''.join(patch))
(p/'base.json').write_text(json.dumps(base,indent=2)+'\n')
(p/'overlay.json').write_text(json.dumps({'Replace':overlay},indent=2)+'\n')
