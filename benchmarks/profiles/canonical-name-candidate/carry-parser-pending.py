from pathlib import Path
import re
out=Path(__file__).resolve().parent
root=out.parents[2]
stage=out/'staged'
module=root/'packages/tsc-go'
def read(rel):
 p=stage/rel
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((module/rel).read_bytes())
 return p,p.read_text()
p,s=read('internal/ast/ast_generated.go')
s=s.replace('func (f *NodeFactory) NewIdentifier(text string) *Node {\n', 'func (f *NodeFactory) NewIdentifier(text string) *Node {\n return f.NewIdentifierName(MakeName(text))\n}\n\nfunc (f *NodeFactory) NewIdentifierName(text Name) *Node {\n',1)
s=s.replace('data.Text = MakeName(text)','data.Text = text',1)
s=s.replace('NewIdentifier(node.Text.String())','NewIdentifierName(node.Text)',1);p.write_text(s)
p,s=read('internal/ast/ast.go')
s,n=re.subn(r'(Identifiers\s+)map\[string\]string',r'\1map[string]Name',s);assert n==1;p.write_text(s)
p,s=read('internal/parser/parser.go')
s,n=re.subn(r'(identifiers\s+)map\[string\]string',r'\1map[string]ast.Name',s);assert n==1
s=s.replace('func (p *Parser) newIdentifier(text string)', 'func (p *Parser) newIdentifier(text ast.Name)')
s=s.replace('p.factory.NewIdentifier(text)', 'p.factory.NewIdentifierName(text)')
s=s.replace('if text == "await" {','if text.String() == "await" {',1)
s=s.replace('p.newIdentifier("")','p.newIdentifier(ast.Name{})')
s=s.replace('p.newIdentifier(p.internIdentifier(text))','p.newIdentifier(p.internIdentifierName(text))')
s=s.replace('func (p *Parser) internIdentifier(text string) string {','func (p *Parser) internIdentifier(text string) string {\n return p.internIdentifierName(text).String()\n}\n\nfunc (p *Parser) internIdentifierName(text string) ast.Name {',1)
s=s.replace('identifier := text\n\tif p.identifiers == nil {','identifier := ast.MakeName(text)\n\tif p.identifiers == nil {',1)
s=s.replace('p.identifiers = make(map[string]string)','p.identifiers = make(map[string]ast.Name)',1)
s=s.replace('p.identifiers[identifier] = identifier','p.identifiers[text] = identifier',1);p.write_text(s)
p,s=read('internal/checker/pending_members.go')
s=s.replace('"slices"','"slices"\n "strings"')
s=s.replace('[]string','[]ast.Name').replace('map[string]int','map[ast.Name]int')
s=s.replace('ownMember(name string)','ownMember(name ast.Name)').replace('get(name string)','get(name ast.Name)')
s=re.sub(r'\.Name\.String\(\s*\)', '.Name',s)
s=s.replace('name.String() != symbol.Name','name != symbol.Name').replace('append(names, name.String())','append(names, name)')
s=s.replace('isReservedMemberName(name)','isReservedMemberName(name.String())')
s=s.replace('getResolvedMember(base.typ, name)','getResolvedMemberKey(base.typ, name)')
s=s.replace('c.isNamedMember(symbol, symbol.Name)', 'c.isNamedMember(symbol, symbol.Name.String())')
s=s.replace('slices.Sort(names)','slices.SortFunc(names, func(a, b ast.Name) int { return strings.Compare(a.String(), b.String()) })')
# Keep the appended string-facing wrapper as a boundary conversion.
body,wrapper=s.split('func getResolvedMember(t *StructuredType, name string)',1)
body=body.replace('ast.MakeName(name)','name')
body=body.replace('name := nameKey.String()\n','').replace('return p.get(name)','return p.get(nameKey)')
s=body+'func getResolvedMember(t *StructuredType, name string)'+wrapper
p.write_text(s)
