"""Build an overlay that coalesces consecutive unrelated declaration assignments."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True, parents=True)
replacements = {}
for name in ("checker.go", "flow.go"):
    path = Path("internal/checker") / name
    src = subprocess.check_output(["git","show",f"78dd830:packages/tsc-go/{path}"],cwd=root,text=True)
    if name == "checker.go":
        src = src.replace("type Checker struct {", "type Checker struct {\n declarationRun declarationRun")
        src = src.replace("c.mergedSymbols[source] = target", "c.declarationRun = declarationRun{}\n c.mergedSymbols[source] = target")
    else:
        src = src.replace("t = c.getTypeAtFlowAssignment(f, flow)", """if flow.Antecedent != nil && flow.Antecedent.Flags&ast.FlowFlagsAssignment != 0 && isPlainDeclarationFlow(flow) {
                if next := c.skipDeclarationRun(f.reference, flow); next != flow {
                    flow = next
                    continue
                }
            }
            t = c.getTypeAtFlowAssignment(f, flow)""")
        at = src.index("func (c *Checker) getTypeAtFlowAssignment")
        src = src[:at]+'''type declarationRun struct {
    base *ast.Symbol
    first, next *ast.FlowNode
}

func isPlainDeclarationFlow(flow *ast.FlowNode) bool {
    if flow == nil || flow.Flags & ^ast.FlowFlagsReferenced != ast.FlowFlagsAssignment {
        return false
    }
    n := flow.Node
    return ast.IsVariableDeclaration(n) && ast.IsIdentifier(n.Name()) &&
        n.Parent != nil && n.Parent.Parent != nil && ast.IsVariableStatement(n.Parent.Parent) &&
        n.Symbol() != nil && n.Symbol().Name != ast.InternalSymbolNameComputed
}

// Only the root identifier of a plain dotted reference can match a variable
// declaration. Each intervening declaration must compare unequal under the
// normal export/merge rules. Stop before every shared node and other flow kind.
func (c *Checker) skipDeclarationRun(ref *ast.Node, first *ast.FlowNode) *ast.FlowNode {
    for ast.IsPropertyAccessExpression(ref) {
        ref = ref.Expression()
    }
    if !ast.IsIdentifier(ref) || ast.IsThisInTypeQuery(ref) {
        return first
    }
    base := c.getExportSymbolOfValueSymbolIfExported(c.getResolvedSymbol(ref))
    if base == nil {
        return first
    }
    previous := c.declarationRun
    next := first
    for isPlainDeclarationFlow(next) {
        if next == previous.first && base == previous.base {
            next = previous.next
            break
        }
        if c.getSymbolOfDeclaration(next.Node) == base {
            break
        }
        next = next.Antecedent
    }
    if next != first {
        c.declarationRun = declarationRun{base, first, next}
    }
    return next
}

'''+src[at:]
    file = out/name
    file.write_text(src)
    replacements[str(root/path)] = str(file)
(out/"overlay.json").write_text(json.dumps({"Replace":replacements}))
