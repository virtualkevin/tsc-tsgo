"""Specialize the generated AST traversal used to set parser parent links."""
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[3] / 'packages/tsc-go'
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
source = (root/'internal/ast/ast_generated.go').read_text()
dispatch = re.search(r'func \(n \*Node\) ForEachChild\(v Visitor\) bool \{(.*?)\n\}', source, re.S)[1]
cases = re.findall(r'case ([^:]+):\n\s*return n\.data\.\(\*(\w+)\)\.ForEachChild\(v\)', dispatch)
assert len(cases) == dispatch.count('case ') and 'default:\n\t\treturn false' in dispatch
lines = ['package ast', '// AssignParserParents returns false for custom traversals handled by the parser visitor.',
         'func AssignParserParents(n *Node) bool {', 'switch n.Kind {']
pattern = r'(visit|visitModifiers|visitNodeList)\(v, node\.(\w+)\)'
specialized = 0
for kinds, concrete in cases:
    body = re.search(r'func \(node \*'+concrete+r'\) ForEachChild\(v Visitor\) bool \{(.*?)\n\}', source, re.S)
    lines.append('case '+kinds+':')
    expr = body[1].strip().removeprefix('return ').split('||') if body else []
    if not expr or not all(re.fullmatch(pattern, term.strip()) for term in expr):
        lines.append('return false')
        continue
    specialized += 1
    lines.append('node := n.data.(*'+concrete+')')
    for term in expr:
        visitor, field = re.fullmatch(pattern,term.strip()).groups()
        access = 'node.'+field
        if visitor == 'visit':
            lines.append(f'if child := {access}; child != nil {{ child.Parent = n }}')
        else:
            lines.append(f'if list := {access}; list != nil {{ for _, child := range list.Nodes {{ child.Parent = n }} }}')
lines += ['}', 'return true','}']
impl = out/'parser_parents.go'
impl.write_text('\n'.join(lines)+'\n')
parser = root/'internal/parser/parser.go'
anchor = 'func (p *Parser) overrideParentInImmediateChildren(node *ast.Node) {'
text = parser.read_text()
assert text.count(anchor)==1
updated = out/'parser.go'
updated.write_text(text.replace(anchor,anchor+'\n if ast.AssignParserParents(node) { return }'))
(out/'overlay.json').write_text(json.dumps({'Replace':{str(root/'internal/ast/parser_parents.go'):str(impl),str(parser):str(updated),str(root/'internal/parser/direct_parents_test.go'):str(Path(__file__).resolve().parent/'parents_test.go.txt')}}))
print(f'Specialized {specialized} of {len(cases)} dispatch arms')
