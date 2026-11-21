"""Overlay the JSX absence filter on the pinned ordinary Go compiler."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
files = {}
def edit(file, changes):
    data = subprocess.check_output(["git","show","bd1baea:packages/tsc-go/"+file],cwd=root,text=True)
    for old, new in changes:
        assert data.count(old) == 1
        data = data.replace(old,new)
    dest = out/Path(file).name
    dest.write_text(data)
    files[str(root/file)] = str(dest)

edit("internal/checker/checker.go", [
    ("type Checker struct {", "type Checker struct {\n jsxMemberFilters map[*Type]*jsxMemberFilter"),
    ("cache[name] = prop\n\t\t// Propagate", """if len(c.jsxMemberFilters) != 0 && !skipObjectFunctionPropertyAugment && cache[name] != nil {
            delete(c.jsxMemberFilters, t)
        }
        cache[name] = prop
        // Propagate""")])
start = "discriminantMembers := core.Filter(c.getPropertiesOfType(contextualType), func(s *ast.Symbol) bool {"
end = "discriminator := &ObjectLiteralDiscriminator{c: c, props: discriminantProperties, members: discriminantMembers}"
edit("internal/checker/jsx.go", [
    (start, """props := c.getPropertiesOfType(contextualType)
    eligible := len(props) >= 32 && node.Symbol() != nil && len(node.Symbol().Members) <= 16
    var discriminantMembers []*ast.Symbol
    if p := c.jsxMemberFilters[contextualType]; eligible && p != nil && p.applies(node,props,jsxChildrenPropertyName) {
        discriminantMembers = p.members
    } else {
    discriminantMembers = core.Filter(props, func(s *ast.Symbol) bool {"""),
    (end, """if eligible { c.rememberJsxFilter(node,contextualType,props,jsxChildrenPropertyName) }
    }
    """+end)])
files[str(root/"internal/checker/jsx_member_filter.go")] = str(here/"filter.go.txt")
if "--observe" in sys.argv:
    path = out/"jsx.go"
    source = path.read_text()
    site = "var discriminantMembers []*ast.Symbol"
    assert source.count(site) == 1
    source = source.replace(site, "if eligible {jsxFilterCounts[0].Add(1)}\n    "+site)
    site = "discriminantMembers = p.members"
    assert source.count(site) == 1
    path.write_text(source.replace(site, """jsxFilterCounts[1].Add(1)
        jsxFilterCounts[2].Add(uint64(len(props)))
        jsxFilterCounts[3].Add(uint64(len(p.members)))
        """+site))
    path = out/"checker.go"
    path.write_text(path.read_text().replace("type Checker struct {", """var jsxFilterCounts [4]atomic.Uint64
func JsxFilterCounts() [4]uint64 {
    var counts [4]uint64
    for i := range counts {counts[i] = jsxFilterCounts[i].Load()}
    return counts
}
type Checker struct {"""))
    edit("cmd/tsgo/main.go", [
        ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
        ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.JsxFilterCounts()); os.Exit(status)")])
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
files[str(root/"internal/checker/jsx_member_filter_test.go")] = str(here/"filter_test.go.txt")
(out/"test-overlay.json").write_text(json.dumps({"Replace":files}))
