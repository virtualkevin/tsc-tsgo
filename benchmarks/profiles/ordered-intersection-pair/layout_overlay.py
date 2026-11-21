"""Reuse validated property name sequences across wide two-constituent reductions."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
repo = here.parents[2]
root = repo / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)

overlay = {}
for file in ["checker.go", "pending_members.go", "lazy_properties.go"]:
    path = root / "internal/checker" / file
    source = subprocess.check_output(["git", "show", "bd1baea:" + str(path.relative_to(repo))], cwd=repo, text=True)
    if file == "checker.go":
        old = "type Checker struct {"
        assert source.count(old) == 1
        source = source.replace(old, old + "\n reductionNames [64][]string")
    elif file == "pending_members.go":
        old = "if names == nil || len(names.names) != len(properties) {"
        assert source.count(old) == 1
        source = source.replace(old, """return names != nil && hasPropertyNames(names.names, properties)
}

func hasPropertyNames(names []string, properties []*ast.Symbol) bool {
    if len(names) != len(properties) {""")
        source = source.replace("if names.names[i] != symbol.Name {", "if names[i] != symbol.Name {")
    else:
        control = out / "original.go"
        control.write_text(source)
        candidate = out / file
        subprocess.run(["patch", "--output", candidate, control, here / "candidate.patch"], check=True)
        source = candidate.read_text()
        source = source.replace("len(properties) > 8 {", "len(properties) > 8 && len(properties) <= 4096 {")
        start = source.index("// A strictly ordered property list")
        end = source.index("apparent := c.getApparentType(skipped)", start)
        source = source[:start] + '''// A plan contains only ordered names. Recheck every name against the current
// symbols since an existing property list may have been exposed or modified.
func (c *Checker) reduceOrderedPair(t, skipped *Type, properties []*ast.Symbol) (bool, bool) {
    slot := &c.reductionNames[len(properties) % len(c.reductionNames)]
    names := *slot
    if !hasPropertyNames(names, properties) {
        seen := make(map[string]struct{}, len(properties))
        names = make([]string, len(properties))
        for i, prop := range properties {
            if _, duplicate := seen[prop.Name]; duplicate {
                return false, false
            }
            seen[prop.Name] = struct{}{}
            names[i] = prop.Name
        }
        *slot = names
    }
    // Calls below can reenter the reducer and replace a slot. Each plan is
    // immutable after publication, and the current symbols are captured here.
    symbols := slices.Clone(properties)
    ''' + source[end:]
        source = source.replace("for _, e := range entries {", "for i, name := range names {")
        source = source.replace("e.name", "name").replace("e.symbol", "symbols[i]")
    dest = out / file
    dest.write_text(source)
    overlay[str(path)] = str(dest)
(out / "overlay.json").write_text(json.dumps({"Replace": overlay}))
