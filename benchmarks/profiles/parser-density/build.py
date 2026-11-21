"""Test adaptive typed-page allocation for common parser nodes in a Go overlay."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
module = here.parents[2]/'packages/tsc-go'
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
overlay = {}
def edit(name, fn):
    p = module/name
    s = p.read_text()
    dest = out/p.name
    updated = fn(s)
    assert updated != s
    dest.write_text(updated)
    overlay[str(p)] = str(dest)
def factory(s):
    s = s.replace('type NodeFactory struct {','type NodeFactory struct {\n parseProgress func() (int, int)')
    for kind in ('identifier','propertyAccessExpression','callExpression','parameterDeclaration','typeReferenceNode','token'):
        anchor = 'f.'+kind+'Arena.New()'
        assert s.count(anchor) == 1
        s = s.replace(anchor, 'f.'+kind+'Arena.NewForSource(f.parseProgress)')
    return s
edit('internal/ast/ast_generated.go',factory)
edit('internal/ast/ast.go',lambda s:s.replace('f.nodeListArena.New()', 'f.nodeListArena.NewForSource(f.parseProgress)')+'''
func (f *NodeFactory) SetParseProgress(progress func() (int,int)) { f.parseProgress = progress }
''')
edit('internal/parser/parser.go',lambda s:s.replace('p.nextToken()\n\tif p.scriptKind == core.ScriptKindJSON', '''p.factory.SetParseProgress(func() (int,int) { return p.nodePos(), len(sourceText) })
    p.nextToken()
    if p.scriptKind == core.ScriptKindJSON''',1))
edit('internal/core/arena.go',lambda s:s+'''
// NewForSource sizes later typed pages using a conservative estimate from the
// current full page and the fraction of source already scanned.
func (a *Arena[T]) NewForSource(progress func() (int,int)) *T {
    if len(a.data) == cap(a.data) { a.growForSource(progress) }
    index := len(a.data)
    a.data = a.data[:index+1]
    return &a.data[index]
}

func (a *Arena[T]) growForSource(progress func() (int,int)) {
    count := len(a.data)
    size := nextArenaSize(count)
    if count >= 16 && progress != nil {
        pos,end := progress()
        if pos > 0 && end > pos {
            // count covers only the latest page. Cap speculative storage
            // and allow more pages when the tail is denser than the prefix.
            estimate := int64(count) * int64(end-pos) / int64(pos)
            size = max(8, int(min(int64(1024),estimate)))
        }
    }
    a.data = slices.Grow[[]T](nil,size)
}
''')
cfg = out/'overlay.json'
cfg.write_text(json.dumps({'Replace':overlay}))
go = sys.argv[2]
core_tests = overlay.copy()
core_tests[str(module/'internal/core/parser_density_test.go')] = str(here/'arena_test.go.txt')
test_config = out/'coretest.json'
test_config.write_text(json.dumps({'Replace':core_tests}))
subprocess.run([go,'test','-overlay='+str(test_config),'-run','^TestSourceDensityPages$','./internal/core'], cwd=module, check=True)
with tempfile.TemporaryDirectory(prefix='parserbench-',dir=module) as tmp:
    tests = Path(tmp)/'parser_test.go'
    tests.write_bytes((here.parent/'parsed-identifier/parser_test.go.txt').read_bytes())
    for engine, opts in [('control',[]),('candidate',['-overlay='+str(cfg)])]:
        subprocess.run([go,'test','-vet=off','-c',*opts,'-o',out/(engine+'.test'),'.'],cwd=tmp,check=True)
