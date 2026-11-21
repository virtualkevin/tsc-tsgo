"""Overlay declaration syntax counters on the pinned pre-experiment compiler."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
files = {}

def replace(path, changes):
    path = Path("packages/tsc-go") / path
    source = subprocess.check_output(["git", "show", f"7d69a8d:{path}"], cwd=root, text=True)
    for before, after in changes:
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    target = out / path.name
    target.write_text(source)
    files[str(root/path)] = str(target)

replace("internal/compiler/fileloader.go", [("\n\treturn sourceFile\n}", """
    if sourceFile != nil && sourceFile.IsDeclarationFile {
        checker.ObserveDeclaration(sourceFile)
    }
    return sourceFile
}"""), ('"cmp"', '"cmp"\n "github.com/microsoft/typescript-go/internal/checker"')])
site = "func (c *Checker) getTypeFromTypeNodeWorker(node *ast.Node) *Type {"
filter_site = "func (c *Checker) removeStringLiteralsMatchedByTemplateLiterals(types []*Type) []*Type {"
filter_start = filter_site + "\n\ttemplates := core.Filter(types, c.isPatternLiteralType)\n\tif len(templates) != 0 {\n\t\ti := len(types)"
filter_end = "return c.isTypeMatchedByTemplateLiteralOrStringMapping(t, template)\n\t\t\t}) {\n\t\t\t\ttypes = slices.Delete(types, i, i+1)\n\t\t\t}\n\t\t}"
replace("internal/checker/checker.go", [
    (filter_start, filter_start + """
        var removed, oldMoves, newMoves int
        candidates.Add(1)
    """),
    (filter_end, """return c.isTypeMatchedByTemplateLiteralOrStringMapping(t, template)
            }) {
                removed++
                oldMoves += len(types)-1-i
                types = slices.Delete(types, i, i+1)
            } else if removed != 0 {
                newMoves++
            }
        }
        if removed != 0 {
            newMoves += len(types)
            removedMembers.Add(uint64(removed))
            oldShifts.Add(uint64(oldMoves))
            compactWrites.Add(uint64(newMoves))
        }"""),
    (site, """
var candidates, removedMembers, oldShifts, compactWrites atomic.Uint64
var declarationFiles sync.Map
var declarationTypes sync.Map

func ObserveDeclaration(file *ast.SourceFile) {
    if _, seen := declarationFiles.LoadOrStore(file, true); seen { return }
    var visit ast.Visitor
    visit = func(n *ast.Node) bool {
        if ast.IsTypeNode(n) { declarationTypes.Store(n, false) }
        n.ForEachChild(visit)
        return false
    }
    file.ForEachChild(visit)
}

type SyntaxCounts struct {
    TemplateFilters, RemovedMembers, OldPointerMoves, CompactPointerWrites uint64
    Files, FileBytes, TypeNodes, RequestedTypeNodes int
    NoWorkerRequestFiles, NoWorkerRequestFileBytes int
    TypeSpanBytes, NoWorkerRequestSpanBytes int
}

func DeclarationDemand() SyntaxCounts {
    counts := SyntaxCounts{TemplateFilters:candidates.Load(), RemovedMembers:removedMembers.Load(), OldPointerMoves:oldShifts.Load(), CompactPointerWrites:compactWrites.Load()}
    declarationFiles.Range(func(key, _ any) bool {
        file := key.(*ast.SourceFile)
        counts.Files++
        counts.FileBytes += len(file.Text())
        // Return whether any inventoried node in this subtree reached the worker.
        // Accumulate disjoint source spans; an unrequested parent subsumes its children.
        var walk func(*ast.Node, bool) bool
        walk = func(n *ast.Node, insideType bool) bool {
            requested := false
            isType := ast.IsTypeNode(n)
            before := counts.NoWorkerRequestSpanBytes
            if isType {
                counts.TypeNodes++
                state, ok := declarationTypes.Load(n)
                if !ok { panic("declaration inventory changed") }
                requested = state.(bool)
                if requested { counts.RequestedTypeNodes++ }
                if !insideType { counts.TypeSpanBytes += n.End()-n.Pos() }
            }
            n.ForEachChild(func(child *ast.Node) bool {
                if walk(child, insideType || isType) { requested = true }
                return false
            })
            if isType && !requested { counts.NoWorkerRequestSpanBytes = before+n.End()-n.Pos() }
            return requested
        }
        before := counts.RequestedTypeNodes
        file.ForEachChild(func(n *ast.Node) bool { walk(n, false); return false })
        if counts.RequestedTypeNodes == before {
            counts.NoWorkerRequestFiles++
            counts.NoWorkerRequestFileBytes += len(file.Text())
        }
        return true
    })
    return counts
}
""" + site + """
    if seen, ok := declarationTypes.Load(node); ok && !seen.(bool) { declarationTypes.Store(node, true) }
""")])
replace("cmd/tsgo/main.go", [('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'), ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.DeclarationDemand()); os.Exit(status)")])
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
