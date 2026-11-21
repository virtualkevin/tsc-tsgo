"""Observe completed keyof-intersection requests without skipping evaluation."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
checker = root / "internal/checker/checker.go"
main = root / "cmd/tsgo/main.go"
source = checker.read_text()
declaration = """type keyofRequest struct {
    intersection *Type
    flags IndexFlags
}
type keyofResult struct {
    first *Type
    active int
}
var keyofCounts [7]atomic.Uint64
func KeyofCounts() []uint64 {
    counts := make([]uint64,len(keyofCounts))
    for i := range counts { counts[i] = keyofCounts[i].Load() }
    return counts
}
type Checker struct {
    keyofRequests map[keyofRequest]*keyofResult
"""
site = "return c.getUnionType(core.Map(t.Types(), func(t *Type) *Type { return c.getIndexTypeEx(t, indexFlags) }))"
assert source.count("type Checker struct {") == source.count(site) == 1
source = source.replace("type Checker struct {", declaration)
source = source.replace(site, """
        if c.keyofRequests == nil { c.keyofRequests = make(map[keyofRequest]*keyofResult) }
        key := keyofRequest{t, indexFlags}
        entry := c.keyofRequests[key]
        keyofCounts[0].Add(1)
        if entry == nil {
            entry = &keyofResult{}
            c.keyofRequests[key] = entry
            keyofCounts[1].Add(1)
        }
        prior := entry.first
        if entry.active > 0 { keyofCounts[4].Add(1) }
        entry.active++
        before := c.TotalInstantiationCount
        result := """ + site.removeprefix("return ") + """
        entry.active--
        if prior != nil {
            keyofCounts[2].Add(1)
            if prior == result { keyofCounts[3].Add(1) }
            if before != c.TotalInstantiationCount { keyofCounts[5].Add(1) }
        }
        if entry.first == nil { entry.first = result }
        if result == c.errorType { keyofCounts[6].Add(1) }
        return result""")
(out / checker.name).write_text(source)
source = main.read_text().replace('"context"', '"context"\n "fmt"\n "github.com/microsoft/typescript-go/internal/checker"')
assert source.count("os.Exit(runMain())") == 1
source = source.replace("os.Exit(runMain())", 'status := runMain(); fmt.Fprintln(os.Stderr,checker.KeyofCounts()); os.Exit(status)')
(out / main.name).write_text(source)
(out / "overlay.json").write_text(json.dumps({"Replace": {str(p): str(out / p.name) for p in (checker, main)}}))
