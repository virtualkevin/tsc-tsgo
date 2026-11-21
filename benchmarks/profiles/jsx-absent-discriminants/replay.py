"""Build an experimental overlay to measure reuse of completed JSX narrowing passes."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
files = {}

def edit(path, old, new):
    source = subprocess.check_output(["git", "show", "21fb142:packages/tsc-go/" + path], cwd=root, text=True)
    assert source.count(old) == 1
    dest = out / Path(path).name
    dest.write_text(source.replace(old, new))
    files[str(root / path)] = str(dest)

edit("internal/checker/checker.go", "type Checker struct {", """type jsxAbsentNarrowing struct {
    members []*ast.Symbol
    result *Type
}
type Checker struct {
    jsxAbsentNarrowings map[*Type]jsxAbsentNarrowing""")

old = "discriminated := c.discriminateTypeByDiscriminableItems(contextualType, discriminator)"
edit("internal/checker/jsx.go", old, """eligible := len(discriminantProperties) == 0 && len(discriminantMembers) != 0 &&
        c.instantiationDepth == 0 && len(c.activeMappers) == 0
    if eligible {
        last := c.jsxAbsentNarrowings[contextualType]
        if last.result != nil && slices.Equal(last.members, discriminantMembers) {
            c.discriminatedContextualTypes[key] = last.result
            return last.result
        }
    }
    """ + old + """
    if eligible {
        if c.jsxAbsentNarrowings == nil {
            c.jsxAbsentNarrowings = make(map[*Type]jsxAbsentNarrowing)
        }
        c.jsxAbsentNarrowings[contextualType] = jsxAbsentNarrowing{
            members: slices.Clone(discriminantMembers),
            result: discriminated,
        }
    }""")
(out / "overlay.json").write_text(json.dumps({"Replace": files}))
