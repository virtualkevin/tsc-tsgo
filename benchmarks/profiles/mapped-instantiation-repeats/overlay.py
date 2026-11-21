"""Measure exact repeat inputs to mapped-property template instantiation."""
from pathlib import Path
import sys
import json

root = Path(__file__).resolve().parents[3]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
overlay = json.loads(Path(sys.argv[2]).read_text())
checker = root/"internal/checker/checker.go"
main = root/"cmd/tsgo/main.go"
s = checker.read_text()
changes = [
    ("type Checker struct {","""type mappedObservationKey struct {
        template, parameter, key *Type
        mapper *TypeMapper
    }
    type mappedObservation struct {
        first *Type
        active uint32
    }
    var mappedRequests, mappedMisses, mappedCalls, mappedFirst, mappedRepeats, mappedEqual, mappedNested, mappedError atomic.Uint64

    func MappedObservations() [8]uint64 {
        return [8]uint64{mappedRequests.Load(), mappedMisses.Load(), mappedCalls.Load(), mappedFirst.Load(), mappedRepeats.Load(), mappedEqual.Load(), mappedNested.Load(), mappedError.Load()}
    }

    type Checker struct {
        mappedObservations map[mappedObservationKey]*mappedObservation"""),
    ("func (c *Checker) getTypeOfMappedSymbol(symbol *ast.Symbol) *Type {\n\tlinks := c.valueSymbolLinks.Get(symbol)\n\tif links.resolvedType == nil {",
     "func (c *Checker) getTypeOfMappedSymbol(symbol *ast.Symbol) *Type {\n mappedRequests.Add(1)\n\tlinks := c.valueSymbolLinks.Get(symbol)\n\tif links.resolvedType == nil {\n mappedMisses.Add(1)"),
    ("""mapper := appendTypeMapping(mappedType.AsMappedType().mapper, c.getTypeParameterFromMappedType(mappedType), c.mappedSymbolLinks.Get(symbol).keyType)
		propType := c.instantiateType(templateType, mapper)""","""outer := mappedType.AsMappedType().mapper
        parameter := c.getTypeParameterFromMappedType(mappedType)
        key := c.mappedSymbolLinks.Get(symbol).keyType
        mapper := appendTypeMapping(outer, parameter, key)
        if c.mappedObservations == nil { c.mappedObservations = make(map[mappedObservationKey]*mappedObservation) }
        descriptor := mappedObservationKey{templateType,parameter,key,outer}
        entry := c.mappedObservations[descriptor]
        if entry == nil {
            entry = &mappedObservation{}
            c.mappedObservations[descriptor] = entry
            mappedFirst.Add(1)
        }
        prior := entry.first
        if entry.active != 0 { mappedNested.Add(1) }
        entry.active++
        propType := c.instantiateType(templateType, mapper)
        entry.active--
        mappedCalls.Add(1)
        if prior != nil {
            mappedRepeats.Add(1)
            if prior == propType { mappedEqual.Add(1) }
        }
        if propType == c.errorType { mappedError.Add(1) }
        if entry.first == nil { entry.first = propType }""")]
for a,b in changes:
    assert s.count(a)==1,a
    s=s.replace(a,b)
(out/checker.name).write_text(s)
s=main.read_text()
s=s.replace('"context"', '"context"\n "fmt"\n "github.com/microsoft/typescript-go/internal/checker"')
assert s.count('os.Exit(runMain())')==1
s=s.replace('os.Exit(runMain())','status := runMain()\n if os.Getenv("TSC_MAPPED_REPORT") != "" { fmt.Fprintln(os.Stderr,checker.MappedObservations()) }; os.Exit(status)')
(out/main.name).write_text(s)
overlay["Replace"].update({str(p):str(out/p.name) for p in (checker,main)})
(out/"overlay.json").write_text(json.dumps(overlay))
