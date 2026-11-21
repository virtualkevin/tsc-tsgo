"""Build the parser's import declaration and its clause in a single typed allocation."""
import json
from pathlib import Path
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
files={}
def load(path):
    return subprocess.check_output(["git","show","50291d2:packages/tsc-go/"+path],cwd=root,text=True)
def save(path,text):
    dest=out/Path(path).name
    dest.write_text(text)
    files[str(root/path)]=str(dest)
def change(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after)

path="internal/ast/ast_generated.go"
s=load(path)
for typ,field,args,names in [
    ("ImportDeclaration","decl","modifiers *ModifierList, importClause *ImportClauseNode, moduleSpecifier *Expression, attributes *ImportAttributesNode","modifiers, importClause, moduleSpecifier, attributes"),
    ("ImportClause","clause","phaseModifier ImportPhaseModifierSyntaxKind, name *IdentifierNode, namedBindings *NamedImportBindings","phaseModifier, name, namedBindings"),
]:
    decl=f"func (f *NodeFactory) New{typ}({args}) *Node {{"
    s=change(s,decl+f"\n\tdata := &{typ}{{}}",decl+f"""
    return f.New{typ}WithPair(nil, {names})
}}

func (f *NodeFactory) New{typ}WithPair(pair *ParserImportPair, {args}) *Node {{
    var data *{typ}
    if pair == nil {{ data = new({typ}) }} else {{ data = &pair.{field} }}""")
save(path,s)
path="internal/ast/ast.go"
save(path,load(path)+'''
// ParserImportPair provides one clause and its enclosing declaration. A parser
// uses each field once, in normal construction order, with no cross-file reuse.
type ParserImportPair struct {
    clause ImportClause
    decl ImportDeclaration
}
''')
path="internal/parser/parser.go"
s=load(path)
s=change(s,"importClause := p.tryParseImportClause(identifier, afterImportPos, phaseModifier, false /*skipJSDocLeadingAsterisks*/)","importClause, pair := p.tryParseImportClause(identifier, afterImportPos, phaseModifier, false /*jsDocImport*/)")
s=change(s,"p.factory.NewImportDeclaration(modifiers, importClause, moduleSpecifier, attributes)","p.factory.NewImportDeclarationWithPair(pair, modifiers, importClause, moduleSpecifier, attributes)")
s=change(s,"tryParseImportClause(identifier *ast.Node, pos int, phaseModifier ast.Kind, skipJSDocLeadingAsterisks bool) *ast.Node","tryParseImportClause(identifier *ast.Node, pos int, phaseModifier ast.Kind, jsDocImport bool) (*ast.Node, *ast.ParserImportPair)")
s=change(s,"importClause := p.parseImportClause(identifier, pos, phaseModifier, skipJSDocLeadingAsterisks)", """var pair *ast.ParserImportPair
        if !jsDocImport {
            pair = new(ast.ParserImportPair)
        }
        importClause := p.parseImportClause(identifier, pos, phaseModifier, jsDocImport, pair)""")
s=change(s,"return importClause\n\t}\n\treturn nil","return importClause, pair\n\t}\n\treturn nil, nil")
s=change(s,"parseImportClause(identifier *ast.Node, pos int, phaseModifier ast.Kind, skipJSDocLeadingAsterisks bool) *ast.Node","parseImportClause(identifier *ast.Node, pos int, phaseModifier ast.Kind, skipJSDocLeadingAsterisks bool, pair *ast.ParserImportPair) *ast.Node")
s=change(s,"p.factory.NewImportClause(phaseModifier, identifier, namedBindings)","p.factory.NewImportClauseWithPair(pair, phaseModifier, identifier, namedBindings)")
save(path,s)
path="internal/parser/jsdoc.go"
s=change(load(path),"importClause := p.tryParseImportClause(","importClause, _ := p.tryParseImportClause(")
save(path,s)
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
