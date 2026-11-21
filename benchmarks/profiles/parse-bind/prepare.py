"""Prepare a go build -overlay file for binding before dependency discovery."""
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = {}

def edit(name, changes):
    path = root / name
    source = path.read_text()
    for old, new in changes:
        assert source.count(old) == 1, (name, old)
        source = source.replace(old, new)
    dest = out / path.name
    dest.write_text(source)
    overlay[str(path)] = str(dest)

edit("internal/compiler/program.go", [
    ("type ProgramOptions struct {", "type ProgramOptions struct {\n BindWhileLoading bool"),
])
edit("internal/compiler/fileloader.go", [
    ('import (', 'import (\n "github.com/microsoft/typescript-go/internal/binder"'),
    ("\n\treturn sourceFile\n}", "\n if p.opts.BindWhileLoading && sourceFile != nil { binder.BindSourceFile(sourceFile) }\n return sourceFile\n}"),
])
# Limit the experiment to the ordinary nonincremental CLI entry point.
name = "internal/execute/tsc.go"
source = (root / name).read_text()
function = source[source.index("func performCompilation("):]
site = "program := compiler.NewProgram(compiler.ProgramOptions{\n\t\tConfig:  config,\n\t\tHost:    host,\n\t\tTracing: tr,\n\t})"
assert function.count(site) == 1
option = "BindWhileLoading: tr == nil && !config.CompilerOptions().ListFilesOnly.IsTrue(),\n Config: config,"
edit(name, [(function, function.replace(site, site.replace("Config:  config,", option)))])
(out / "overlay.json").write_text(json.dumps({"Replace": overlay}))
