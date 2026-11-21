"""Pass the embedded node to the shared initializer from each concrete factory."""
import difflib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
module = root / 'packages/tsc-go'
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = {}
patch = []
for name in ('ast.go', 'ast_generated.go'):
    path = module / 'internal/ast' / name
    src = path.read_text()
    changed, count = re.subn(r'f\.newNode\((\w+), data\)', r'f.newConcreteNode(\1, data.AsNode(), data)', src)
    assert count == (1 if name == 'ast.go' else 193), count
    if name == 'ast.go':
        changed = changed.replace('n := data.AsNode()', '''return initializeNode(kind, data.AsNode(), data, hooks)
}

func initializeNode(kind Kind, n *Node, data nodeData, hooks NodeFactoryHooks) *Node {''', 1)
        changed = changed.replace('func (f *NodeFactory) newNode(kind Kind, data nodeData)', 'func (f *NodeFactory) newConcreteNode(kind Kind, n *Node, data nodeData)')
        changed = changed.replace('return newNode(kind, data, f.hooks)', 'return initializeNode(kind, n, data, f.hooks)')
    dest = out / name
    dest.write_text(changed)
    overlay[str(path)] = str(dest)
    rel = str(path.relative_to(root))
    patch.extend(difflib.unified_diff(src.splitlines(True), changed.splitlines(True), 'a/'+rel, 'b/'+rel))
(out/'candidate.patch').write_text(''.join(patch))
test = module/'internal/parser/parsed_identifier_test.go'
overlay[str(test)] = str(here.parent/'parsed-identifier/parser_test.go.txt')
cfg = out/'overlay.json'
cfg.write_text(json.dumps({'Replace':overlay}))
control = out/'control-overlay.json'
control.write_text(json.dumps({'Replace':{str(test):overlay[str(test)]}}))
for engine, config in [('control',control),('candidate',cfg)]:
    checks = json.loads(config.read_text())['Replace']
    checks[str(module/'internal/ast/concrete_factory_test.go')] = str(here/'hooks_test.go.txt')
    hooks = out/(engine+'-hooks.json')
    hooks.write_text(json.dumps({'Replace':checks}))
    subprocess.run([sys.argv[2],'test','-overlay='+str(hooks),'-run','^TestConcreteFactoryPublication$','./internal/ast'], cwd=module, check=True)
    subprocess.run([sys.argv[2], 'test', '-c', '-vet=off', '-overlay='+str(config), '-o', out/(engine+'.test'), './internal/parser'], cwd=module, check=True)
