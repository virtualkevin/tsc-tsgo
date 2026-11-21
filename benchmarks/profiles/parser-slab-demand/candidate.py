"""Generate a front-end experiment with typed first pages sharing one per-file allocation."""
from pathlib import Path
import json
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
config=json.loads((here/"model.json").read_text())["configurations"][sys.argv[2]]
cutoff=int(sys.argv[3])
files={}
def edit(name, transform):
    path=root/name
    old=subprocess.check_output(["git","show","50291d2:packages/tsc-go/"+name],cwd=root,text=True)
    updated=transform(old)
    assert updated!=old
    p=out/path.name
    p.write_text(updated)
    files[str(path)]=str(p)
edit("internal/core/arena.go",lambda s:s+'''
// ArenaWithStorage starts with caller-owned, zeroed storage. Its backing array
// must be used exclusively by this arena for the lifetime of its elements.
func ArenaWithStorage[T any](storage []T) Arena[T] { return Arena[T]{data: storage[:0]} }
''')
fields={t:t[0].lower()+t[1:] for t in config}
source='''package ast
import "github.com/microsoft/typescript-go/internal/core"

// Each field has a concrete GC pointer layout. Nodes retain stable addresses
// after an individual arena grows out of the shared allocation.
type parserFirstPages struct {
'''
for t,n in config.items():
    source+=f" {fields[t]} [{n}]{t}\n"
source+='''}
// StartParserArenas is called once on a fresh per-file factory.
func (f *NodeFactory) StartParserArenas() {
    pages := new(parserFirstPages)
'''
for t,field in fields.items():
    # JSDoc fields are spelled jsdoc... in the generated factory.
    field=field.replace("jSDoc","jsdoc")
    source+=f" f.{field}Arena = core.ArenaWithStorage(pages.{fields[t]}[:])\n"
source+="}\n"
addition=out/"parser_first_pages.go"
addition.write_text(source)
files[str(root/"internal/ast/parser_first_pages.go")]=str(addition)
site="p := getParser()\n\tdefer putParser(p)\n\tp.initializeState(opts, sourceText, scriptKind)"
def parser(src):
    assert src.count(site)==1
    return src.replace(site,site+f"\n if len(sourceText)>={cutoff} {{ p.factory.StartParserArenas() }}")
edit("internal/parser/parser.go",parser)
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
