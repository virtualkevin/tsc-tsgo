"""Generate an isolated instrumented compiler without modifying production source."""
from pathlib import Path
import json
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / 'packages/tsc-go'
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
replace = {}

def edit(name, substitutions):
    path = root / name
    text = path.read_text()
    for before, after in substitutions:
        assert text.count(before) == 1
        text = text.replace(before, after)
    target = out / path.name
    target.write_text(text)
    replace[str(path)] = str(target)

edit('internal/checker/checker.go', [
    ('func (c *Checker) getMembersOfSymbol(symbol *ast.Symbol) ast.SymbolTable {',
     'func (c *Checker) getMembersOfSymbol(symbol *ast.Symbol) ast.SymbolTable {\n observeInterface(symbol, &memberRequests)'),
    ('func (c *Checker) mergeSymbol(target *ast.Symbol, source *ast.Symbol, unidirectional bool) *ast.Symbol {',
     'func (c *Checker) mergeSymbol(target *ast.Symbol, source *ast.Symbol, unidirectional bool) *ast.Symbol {\n observeInterface(target, &mergeRequests)\n observeInterface(source, &mergeRequests)')])
edit('internal/compiler/checkerpool.go', [('checkerCount := 4', 'interfaceProgram = program\n\tcheckerCount := 4')])
edit('cmd/tsgo/main.go', [('import (','import (\n "github.com/microsoft/typescript-go/internal/compiler"'),
                         ('return int(result.Status)', 'compiler.ReportInterfaceDemand()\n return int(result.Status)')])
for pkg in ['compiler','checker']:
    replace[str(root / f'internal/{pkg}/interface_probe.go')] = str(here / f'{pkg}.go.txt')
(out / 'overlay.json').write_text(json.dumps({'Replace': replace}))
