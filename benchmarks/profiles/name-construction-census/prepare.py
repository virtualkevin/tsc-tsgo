from pathlib import Path
import difflib,json
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
replace={};patch=[]
def save(rel,s):
 p=root/rel;original=p.read_text();target=out/'overlay-source'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(s);replace[str(p)]=str(target)
 patch.extend(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
for rel,needle,hook in [
 ('packages/tsc-go/internal/ast/ast_generated.go','func (f *NodeFactory) NewIdentifier(text string) *Node {','ObserveNameConstruction(NameConstructionIdentifier, text)'),
 ('packages/tsc-go/internal/binder/binder.go','func (b *Binder) newSymbol(flags ast.SymbolFlags, name string) *ast.Symbol {','ast.ObserveNameConstruction(ast.NameConstructionBinderSymbol, name)'),
 ('packages/tsc-go/internal/checker/checker.go','func (c *Checker) newSymbol(flags ast.SymbolFlags, name string) *ast.Symbol {','ast.ObserveNameConstruction(ast.NameConstructionCheckerSymbol, name)')]:
 s=(root/rel).read_text();assert s.count(needle)==1;save(rel,s.replace(needle,needle+'\n '+hook,1))
p='packages/tsc-go/cmd/tsgo/main.go';s=(root/p).read_text().replace('"context"','"context"\n "fmt"\n "github.com/microsoft/typescript-go/internal/ast"')
s=s.replace('return int(result.Status)','if err := ast.WriteNameConstructionCensus(); err != nil {fmt.Fprintln(os.Stderr,err);return 1}\n return int(result.Status)');save(p,s)
for src,name in [('census.go','name_construction_census.go'),('census_test.go','name_construction_census_test.go')]:
 p=root/'packages/tsc-go/internal/ast'/name;assert not p.exists();replace[str(p)]=str(out/src)
(out/'overlay.json').write_text(json.dumps({'Replace':replace},indent=2)+'\n');(out/'instrumentation.patch').write_text(''.join(patch))
