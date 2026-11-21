"""Count individual typed arena allocations in the parser's per-file factory."""
from pathlib import Path
import json
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
sources = {}
def read(path):
    return subprocess.check_output(["git","show","50291d2:packages/tsc-go/"+path],cwd=root,text=True)
def emit(path, source):
    dest = out / Path(path).name
    dest.write_text(source)
    sources[str(root/path)] = str(dest)

path = "internal/ast/ast_generated.go"
generated = read(path)
kinds = re.findall(r'^\s*(\w+Arena)\s+core\.Arena\[(\w+)\]$',generated,re.M)
indices = {name:i for i,(name,_) in enumerate(kinds)}
seen = set()
def instrument(source):
    def replace(m):
        name = m[3]
        seen.add(name)
        return f"{m[1]}f.parserArenaCounts[{indices[name]}]++\n{m[0]}"
    return re.sub(r'^(\s*)(\w+) := f\.(\w+Arena)\.New\(\)$', replace, source, flags=re.M)
generated = generated.replace('type NodeFactory struct {','type NodeFactory struct {\n parserArenaCounts ['+str(len(kinds))+']int')
emit(path,instrument(generated))
path = "internal/ast/ast.go"
source = read(path)
assert '"unsafe"' in source or 'import (' in source
if '"unsafe"' not in source:
    source = source.replace('import (','import (\n "unsafe"',1)
source = instrument(source)
source += """
func (f *NodeFactory) ParserArenaCounts() []int { return f.parserArenaCounts[:] }
func ParserArenaSizes() []uintptr { return []uintptr{""" + ",".join("unsafe.Sizeof("+typ+"{})" for _,typ in kinds) + "} }\n"
assert seen == set(indices)
emit(path,source)
path = "internal/parser/parser.go"
source = read(path)
for pkg in ("encoding/json","os","fmt"):
    if f'"{pkg}"' not in source:
        source=source.replace("import (",f'import (\n "{pkg}"',1)
anchor="result.IdentifierCount = p.identifierCount"
assert source.count(anchor)==1
source = source.replace(anchor,anchor+"""
    row, err := json.Marshal([]any{p.opts.FileName, len(p.sourceText), p.factory.ParserArenaCounts()})
    if err != nil { panic(err) }
    fmt.Fprintln(os.Stderr,string(row))""")
emit(path,source)
path = "cmd/tsgo/main.go"
source = read(path).replace('"context"','"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/ast"')
source = source.replace("os.Exit(runMain())","json.NewEncoder(os.Stderr).Encode(ast.ParserArenaSizes()); os.Exit(runMain())")
emit(path,source)
(out/"overlay.json").write_text(json.dumps({"Replace":sources}))
(out/"types.json").write_text(json.dumps([typ for _,typ in kinds]))
