"""Generate an observer overlay after applying candidate.patch to revision 7d69a8d."""
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[3]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
shadow="--shadow" in sys.argv[2:]
checker=root/"internal/checker/checker.go"
store=root/"internal/core/pointerlinkstore.go"
main=root/"cmd/tsgo/main.go"
s=checker.read_text()
site="func (c *Checker) getTypeOfSymbol(symbol *ast.Symbol) *Type {"
assert s.count(site)==1
s=s.replace(site,"""var symbolRequests, eligibleReads, resolvedReads atomic.Uint64
func SymbolReadCounts() [4]uint64 {
    return [4]uint64{symbolRequests.Load(), eligibleReads.Load(), resolvedReads.Load(), core.SlotHits.Load()}
}
"""+site+"\n symbolRequests.Add(1)")
site="if symbol.CheckFlags&linkedChecks != 0 || symbol.Flags&linkedKinds != 0 {"
assert s.count(site)==1
s=s.replace(site,site+"\n eligibleReads.Add(1)")
site="if links := c.valueSymbolLinks.TryGetWithHints(symbol, &c.symbolReadHints); links != nil && links.resolvedType != nil {"
assert s.count(site)==1
s=s.replace(site,site+"\n resolvedReads.Add(1)")
if shadow:
    s=s.replace("var symbolRequests, eligibleReads, resolvedReads atomic.Uint64",
                "var symbolRequests, eligibleReads, resolvedReads, resultDiffs, workDiffs atomic.Uint64")
    s=s.replace("[4]uint64","[6]uint64").replace("core.SlotHits.Load()}","core.SlotHits.Load(),resultDiffs.Load(),workDiffs.Load()}")
    hit="resolvedReads.Add(1)\n\t\t\treturn links.resolvedType"
    assert s.count(hit)==1
    s=s.replace(hit,"""resolvedReads.Add(1)
        predicted := links.resolvedType
        types,symbols,instantiations := c.TypeCount,c.SymbolCount,c.TotalInstantiationCount
        actual := c.symbolReadOracle(symbol)
        if predicted != actual { resultDiffs.Add(1) }
        if types != c.TypeCount || symbols != c.SymbolCount || instantiations != c.TotalInstantiationCount { workDiffs.Add(1) }
        return actual""")
    boundary="\n\tif symbol.CheckFlags&ast.CheckFlagsDeferredType != 0 {"
    start=s.index("func (c *Checker) getTypeOfSymbol(symbol")
    pos=s.index(boundary,start)
    s=s[:pos]+"""
        return c.symbolReadOracle(symbol)
    }
    func (c *Checker) symbolReadOracle(symbol *ast.Symbol) *Type {"""+s[pos:]
(out/checker.name).write_text(s)
s=store.read_text().replace("type PointerSlotHints [1024]atomic.Uint32","var SlotHits atomic.Uint64\ntype PointerSlotHints [1024]atomic.Uint32")
site="if entry.key == key && entry.value != nil {"
assert s.count(site)==1
(out/store.name).write_text(s.replace(site,site+"\n SlotHits.Add(1)"))
s=main.read_text().replace('"context"', '"context"\n "fmt"\n "github.com/microsoft/typescript-go/internal/checker"')
(out/main.name).write_text(s.replace("os.Exit(runMain())","status := runMain(); fmt.Fprintln(os.Stderr,checker.SymbolReadCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":{str(f):str(out/f.name) for f in (checker,store,main)}}))
