"""Skip a redundant membership search when every input is a named primitive union."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
go = sys.argv[2]
checker = root / "internal/checker/checker.go"
source = checker.read_text()
start = source.index("for _, t := range typeSet {", source.index("namedUnions := c.addNamedUnions(nil, types)"))
end = source.index("\n\t\tif alias == nil", start)
loop = source[start:end]
assert "reducedTypes = append(reducedTypes, t)" in loop
source = source[:start] + """// Literal reduction only removes members. When every input is itself a named,
        // canonical primitive union, each surviving member came from one of them.
        if unionReduction != UnionReductionLiteral || !core.Every(types, isNamedPrimitiveUnion) {
            """ + loop + "\n        }" + source[end:]
marker = "func (c *Checker) addNamedUnions("
assert source.count(marker) == 1
source = source.replace(marker, """func isNamedPrimitiveUnion(t *Type) bool {
    if t.flags&TypeFlagsUnion == 0 || t.objectFlags&ObjectFlagsPrimitiveUnion == 0 { return false }
    origin := t.AsUnionType().origin
    return t.alias != nil || origin != nil && origin.flags&TypeFlagsUnion == 0
}

""" + marker)
dest = out / "checker.go"
dest.write_text(source)
files = {str(checker): str(dest)}
cfg = out / "overlay.json"
cfg.write_text(json.dumps({"Replace": files}))
subprocess.run([go, "build", "-buildvcs=false", "-overlay=" + str(cfg), "-o", out / "tsgo", "./cmd/tsgo"], cwd=root, check=True)
ordinary = checker.read_text()
start = ordinary.index("func (c *Checker) getUnionTypeWorker(")
end = ordinary.index("// This function assumes the constituent type list", start)
body = ordinary[start:end].replace("getUnionTypeWorker(", "ordinaryUnionWorker(", 1)
oracle = out / "ordinary_test.go"
oracle.write_text('package checker\nimport ("slices"; "github.com/microsoft/typescript-go/internal/core")\n' + body)
files[str(checker.parent / "ordinary_union_test.go")] = str(oracle)
files[str(checker.parent / "named_key_test.go")] = str(here / "union_test.go.txt")
tests = out / "test-overlay.json"
tests.write_text(json.dumps({"Replace": files}))
subprocess.run([go, "test", "-overlay=" + str(tests), "-count=1", "./internal/checker", "./internal/compiler", "./internal/execute"], cwd=root, check=True)
