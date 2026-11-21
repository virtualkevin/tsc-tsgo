"""Build candidate or observer overlays for anonymous object instantiation."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True, parents=True)
mode = sys.argv[2]
assert mode in ("candidate", "observer")
replacements = {}

def source(path):
    return subprocess.check_output(["git","show","0a28a53:packages/tsc-go/"+path], cwd=root, text=True)

def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)

def save(path, text):
    p = out / Path(path).name
    p.write_text(text)
    replacements[str(root/path)] = str(p)

path = "internal/checker/checker.go"
s = source(path)
start = s.index("func (c *Checker) getObjectTypeInstantiation(")
end = s.index("func (c *Checker) isTypeParameterPossiblyReferenced",start)
body = s[start:end]
if mode == "candidate":
    body = replace(body, """combinedMapper := c.combineTypeMappers(t.Mapper(), m)
	typeArguments := make([]*Type, len(typeParameters))
	for i, tp := range typeParameters {
		typeArguments[i] = combinedMapper.Map(tp)
	}""", """var small [4]*Type
	var typeArguments, heapArguments []*Type
	if len(typeParameters) <= len(small) {
		typeArguments = small[:len(typeParameters)]
	} else {
		heapArguments = make([]*Type, len(typeParameters))
		typeArguments = heapArguments
	}
	if prior := t.Mapper(); prior != nil {
		combined := CompositeTypeMapper{c: c, m1: prior, m2: m}
		for i, tp := range typeParameters {
			typeArguments[i] = combined.Map(tp)
		}
	} else {
		for i, tp := range typeParameters {
			typeArguments[i] = m.Map(tp)
		}
	}""")
    body = replace(body, """newAlias := alias
	if newAlias == nil {
		newAlias = c.instantiateTypeAlias(t.alias, m)
	}""", """var mappedAlias TypeAlias
	keyAlias := alias
	if original := t.alias; keyAlias == nil && original != nil {
		mappedAlias = TypeAlias{symbol: original.symbol, typeArguments: c.instantiateTypes(original.typeArguments, m)}
		keyAlias = &mappedAlias
	}""")
    body = replace(body, "getTypeInstantiationKey(typeArguments, newAlias,", "getTypeInstantiationKey(typeArguments, keyAlias,")
    body = replace(body, "newMapper := newTypeMapper(typeParameters, typeArguments)", """var newMapper *TypeMapper
		if len(typeParameters) == 1 {
			newMapper = newSimpleTypeMapper(typeParameters[0], typeArguments[0])
		} else {
			// The mapper retains its targets after this call.
			if len(typeParameters) <= len(small) {
				newMapper = newArrayTypeMapper(typeParameters, slices.Clone(typeArguments))
			} else {
				newMapper = newArrayTypeMapper(typeParameters, heapArguments)
			}
		}
		newAlias := alias
		if keyAlias == &mappedAlias {
			newAlias = &TypeAlias{symbol: mappedAlias.symbol, typeArguments: mappedAlias.typeArguments}
		}""")
else:
    body = replace(body, "result := data.instantiations[key]", """result := data.instantiations[key]
	var mask int
	if result != nil {mask |= 1}
	if t.Mapper() != nil {mask |= 2}
	if alias == nil && t.alias != nil {mask |= 4}
	objectInstantiationCounts[min(len(typeParameters), 5)][mask].Add(1)""")
s = s[:start]+body+s[end:]
if mode=="observer":
    s += """
var objectInstantiationCounts [6][8]atomic.Uint64
func ObjectInstantiationCounts() (out [6][8]uint64) {
    for i:=range out {for j:=range out[i] {out[i][j]=objectInstantiationCounts[i][j].Load()}}
    return out
}
"""
    main = "cmd/tsgo/main.go"
    t = replace(source(main), '"context"', '"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
    save(main,replace(t,"os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.ObjectInstantiationCounts()); os.Exit(status)"))
save(path,s)
(out/"overlay.json").write_text(json.dumps({"Replace":replacements}))

test = root/"internal/checker/object_hit_test.go"
test_replacements = {str(test):str(here/"object_test.go.txt")}
(out/"test-overlay.json").write_text(json.dumps({"Replace":{**replacements,**test_replacements}}))
(out/"control-test-overlay.json").write_text(json.dumps({"Replace":test_replacements}))
