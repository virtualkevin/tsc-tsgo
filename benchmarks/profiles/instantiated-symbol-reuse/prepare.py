"""Measure reuse on wrapper-cache misses without replacing compiler results."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True, parents=True)
replacements = {}

def source(name):
    return subprocess.check_output(["git", "show", "28cf608:packages/tsc-go/" + name], cwd=root, text=True)

def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)

def save(name, text):
    file = out / Path(name).name
    file.write_text(text)
    replacements[str(root/name)] = str(file)

name = "internal/checker/checker.go"
s = replace(source(name), "type Checker struct {", """type observedSubstitution struct {
    symbol *ast.Symbol
    input, from, to *Type
    mapper *TypeMapper
}
type observedResult struct {
    owner *ast.Symbol
    result *Type
}
var observedSubstitutions [3][7]atomic.Uint64
func ObservedSubstitutions() (counts [3][7]uint64) {
    for k := range counts {
        for i := range counts[k] { counts[k][i] = observedSubstitutions[k][i].Load() }
    }
    return counts
}
func (c *Checker) observeSubstitution(kind int, key observedSubstitution, owner *ast.Symbol, result *Type, work uint64) {
    seen := c.symbolSubstitutions[kind]
    if seen == nil {
        seen = make(map[observedSubstitution]observedResult)
        c.symbolSubstitutions[kind] = seen
    }
    counts := &observedSubstitutions[kind]
    counts[0].Add(1)
    counts[1].Add(work)
    if prev, ok := seen[key]; ok && prev.owner != owner {
        counts[2].Add(1)
        counts[3].Add(work)
        if prev.result != result { counts[4].Add(1) }
        if work != 0 { counts[5].Add(1) }
    }
    if len(seen) >= 32768 { clear(seen); counts[6].Add(1) }
    seen[key] = observedResult{owner, result}
}
type Checker struct {
    symbolSubstitutions [3]map[observedSubstitution]observedResult""")
s = replace(s, "links.resolvedType = c.instantiateType(c.getTypeOfSymbol(links.target), links.mapper)", """target := links.target
        input := c.getTypeOfSymbol(target)
        mapper := links.mapper
        before := c.TotalInstantiationCount
        result := c.instantiateType(input, mapper)
        links.resolvedType = result
        work := uint64(c.TotalInstantiationCount - before)
        c.observeSubstitution(0, observedSubstitution{symbol:target, mapper:mapper},symbol,result,work)
        c.observeSubstitution(1, observedSubstitution{input:input, mapper:mapper},symbol,result,work)
        if mapper != nil {
            if simple,ok := mapper.data.(*SimpleTypeMapper); ok {
                c.observeSubstitution(2, observedSubstitution{input:input, from:simple.source, to:simple.target},symbol,result,work)
            }
        }""")
save(name, s)
name = "cmd/tsgo/main.go"
s = replace(source(name), '"context"', '"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
save(name, replace(s, "os.Exit(runMain())", "status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.ObservedSubstitutions()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":replacements}))
