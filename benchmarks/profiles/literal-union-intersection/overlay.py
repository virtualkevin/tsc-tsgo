"""Construct a plain string literal intersection experiment or an observing control."""
import argparse
import json
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mode", choices=("candidate", "observe"))
parser.add_argument("out", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
out = args.out.resolve()
out.mkdir(exist_ok=True, parents=True)
files = {}

def read(name):
    return subprocess.check_output(["git", "show", f"50291d2:packages/tsc-go/{name}"], cwd=root, text=True)

def save(name, source):
    target = out / Path(name).name
    target.write_text(source)
    files[str(root / "packages/tsc-go" / name)] = str(target)

checker = "internal/checker/checker.go"
s = read(checker)
site = "\t// We have more than one union of primitive types, now intersect them."
assert s.count(site) == 1
guard = """len(unionTypes) == 2 && len(unionTypes[0].Types()) + len(unionTypes[1].Types()) >= 64 &&
        allPlainStringLiterals(unionTypes[0].Types()) && allPlainStringLiterals(unionTypes[1].Types())"""
helpers = """
func allPlainStringLiterals(types []*Type) bool {
    for _, t := range types {
        if t.flags != TypeFlagsStringLiteral { return false }
    }
    return true
}
"""
if args.mode == "candidate":
    work = """
        left, right := unionTypes[0].Types(), unionTypes[1].Types()
        var result []*Type
        for len(left) != 0 && len(right) != 0 {
            switch order := CompareTypes(left[0], right[0]); {
            case order < 0: left = left[1:]
            case order > 0: right = right[1:]
            default:
                result = append(result, left[0])
                left, right = left[1:], right[1:]
            }
        }
        types[index] = c.getUnionTypeFromSortedList(result, ObjectFlagsPrimitiveUnion, nil, nil)
        return types, true
"""
else:
    helpers += """
var primitiveIntersectionCalls, literalIntersectionPairs, literalIntersectionMembers atomic.Uint64
func IntersectionCounts() [3]uint64 {
    return [3]uint64{primitiveIntersectionCalls.Load(), literalIntersectionPairs.Load(), literalIntersectionMembers.Load()}
}
"""
    work = """
        literalIntersectionPairs.Add(1)
        literalIntersectionMembers.Add(uint64(len(unionTypes[0].Types()) + len(unionTypes[1].Types())))
"""
    site_prelude = "\tprimitiveIntersectionCalls.Add(1)\n"
    s = s.replace(site, site_prelude + site)
    main = "cmd/tsgo/main.go"
    m = read(main)
    assert m.count("os.Exit(runMain())") == 1
    save(main, m.replace('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"').replace("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.IntersectionCounts()); os.Exit(status)"))
save(checker, s.replace(site, "\tif " + guard + " {" + work + "\t}\n" + site) + helpers)
(out / "overlay.json").write_text(json.dumps({"Replace": files}))
