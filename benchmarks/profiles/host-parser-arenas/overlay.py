"""Generate the host-local parser arena reuse experiment."""
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/'packages/tsc-go'
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
replace = {}

def edit(name, substitutions):
    path = root/name
    source = path.read_text()
    for before, after in substitutions:
        assert source.count(before)==1, before
        source = source.replace(before,after)
    target = out/path.name
    target.write_text(source)
    replace[str(path)] = str(target)

edit('internal/ast/ast.go',[('func (f *NodeFactory) NodeCount() int {','''// ContinueFileAllocation resets per-file accounting and keeps only the
// factory's current typed slabs. Published nodes and slices are never reset.
func (f *NodeFactory) ContinueFileAllocation() {
	f.hooks = NodeFactoryHooks{}
	f.nodeCount = 0
	f.textCount = 0
}

func (f *NodeFactory) NodeCount() int {''')])
prefix='func ParseSourceFile(opts ast.SourceFileParseOptions, sourceText string, scriptKind core.ScriptKind) *ast.SourceFile {'
edit('internal/parser/parser.go',[(prefix,'''// BatchParsers gives one compiler host exclusive reusable parser instances.
type BatchParsers struct {
	parsers sync.Pool
}

func (batch *BatchParsers) ParseSourceFile(opts ast.SourceFileParseOptions, sourceText string, scriptKind core.ScriptKind) *ast.SourceFile {
	p, _ := batch.parsers.Get().(*Parser)
	if p == nil {
		p = newParser()
	}
	file := p.parseFile(opts, sourceText, scriptKind)
	p.factory.ContinueFileAllocation()
	*p = Parser{factory: p.factory, scanner: p.scanner, setParentFromContext: p.setParentFromContext}
	batch.parsers.Put(p)
	return file
}

'''+prefix), ('defer putParser(p)\n\tp.initializeState(opts, sourceText, scriptKind)\n\tp.nextToken()\n\tif p.scriptKind == core.ScriptKindJSON', '''defer putParser(p)
	return p.parseFile(opts, sourceText, scriptKind)
}

func (p *Parser) parseFile(opts ast.SourceFileParseOptions, sourceText string, scriptKind core.ScriptKind) *ast.SourceFile {
	p.initializeState(opts, sourceText, scriptKind)
	p.nextToken()
	if p.scriptKind == core.ScriptKindJSON''')])
edit('internal/compiler/host.go',[('type compilerHost struct {','type compilerHost struct {\n batch parser.BatchParsers'),
    ('return parser.ParseSourceFile(opts, text, core.GetScriptKindFromFileName(opts.FileName))',
     'return h.batch.ParseSourceFile(opts, text, core.GetScriptKindFromFileName(opts.FileName))')])
replace[str(root/'internal/parser/batch_arenas_test.go')]=str(here/'batch_test.go.txt')
replace[str(root/'internal/ast/slab_retention_test.go')]=str(here/'retention_test.go.txt')
(out/'overlay.json').write_text(json.dumps({'Replace':replace}))
