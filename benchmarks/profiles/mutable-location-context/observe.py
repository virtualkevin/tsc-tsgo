"""Observe both contextual lookups in a single mutable-location check."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = {}

def patch(file, edits):
    source = subprocess.check_output(["git", "show", f"bd1baea:packages/tsc-go/{file}"], cwd=root, text=True)
    for old, new in edits:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    if file == "internal/checker/checker.go" and "--quoted-jsx" in sys.argv:
        # Count only quoted attributes. All nodes still execute the original lookups.
        source = source.replace("mutableCounts[0].Add(1)", """quoted := node.Kind == ast.KindStringLiteral && ast.IsJsxAttribute(node.Parent)
        if quoted { mutableCounts[0].Add(1) }""")
        source = source.replace("if obs.seen {", "if obs.seen && quoted {")
    path = out / Path(file).name
    path.write_text(source)
    overlay[str(root/file)] = str(path)

signature = "func (c *Checker) isConstContext(node *ast.Node) bool {"
patch("internal/checker/checker.go", [
    (signature, """type mutableObservation struct { seen bool; first *Type }
var mutableCounts [9]atomic.Uint64
func MutableCounts() [9]uint64 {
    var counts [9]uint64
    for i := range counts { counts[i] = mutableCounts[i].Load() }
    return counts
}
""" + signature + """
    return c.observeConstContext(node, nil)
}
func (c *Checker) observeConstContext(node *ast.Node, obs *mutableObservation) bool {"""),
    ("c.isConstTypeVariable(c.getContextualType(node, ContextFlagsNone), 0) ||",
     """func() bool {
         t := c.getContextualType(node, ContextFlagsNone)
         if obs != nil { obs.seen = true; obs.first = t }
         return c.isConstTypeVariable(t, 0)
     }() ||"""),
    ("t := c.checkExpressionEx(node, checkMode)\n\tswitch {\n\tcase c.isConstContext(node):",
     """t := c.checkExpressionEx(node, checkMode)
     var obs mutableObservation
     switch {
     case c.observeConstContext(node, &obs):"""),
    ("return c.getWidenedLiteralLikeTypeForContextualType(t, c.instantiateContextualType(c.getContextualType(node, ContextFlagsNone), node, ContextFlagsNone))",
     """mutableCounts[0].Add(1)
     inst, types, symbols := c.TotalInstantiationCount, c.TypeCount, c.SymbolCount
     budget := c.instantiationCount
     assignable, subtype := c.assignableRelation.size(), c.subtypeRelation.size()
     second := c.getContextualType(node, ContextFlagsNone)
     if obs.seen {
         mutableCounts[1].Add(1)
         if second != obs.first {mutableCounts[2].Add(1)}
         if c.TotalInstantiationCount != inst {mutableCounts[3].Add(1)}
         if c.TypeCount != types {mutableCounts[4].Add(1)}
         if c.SymbolCount != symbols {mutableCounts[5].Add(1)}
         if c.instantiationCount != budget {mutableCounts[6].Add(1)}
         if assignable != c.assignableRelation.size() || subtype != c.subtypeRelation.size() {mutableCounts[7].Add(1)}
         if second == nil {mutableCounts[8].Add(1)}
     }
     return c.getWidenedLiteralLikeTypeForContextualType(t, c.instantiateContextualType(second, node, ContextFlagsNone))""")
])
patch("cmd/tsgo/main.go", [('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.MutableCounts()); os.Exit(status)")])
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
