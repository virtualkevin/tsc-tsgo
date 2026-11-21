"""Observe existing intersection-property cache entries before each absent JSX lookup."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
files = {}
def edit(file, old, new):
    s = subprocess.check_output(["git","show","21fb142:packages/tsc-go/"+file], cwd=root, text=True)
    assert s.count(old) == 1
    dest = out / Path(file).name
    dest.write_text(s.replace(old,new))
    files[str(root/file)] = str(dest)

edit("internal/checker/checker.go", "type ObjectLiteralDiscriminator struct {", """var jsxCellCounts [8][6]atomic.Uint64
var jsxPassCounts [2][2]atomic.Uint64
func JsxCellCounts() map[string][][]uint64 {
    cells := make([][]uint64, len(jsxCellCounts))
    for i := range cells {
        for j := range jsxCellCounts[i] { cells[i] = append(cells[i], jsxCellCounts[i][j].Load()) }
    }
    passes := make([][]uint64, len(jsxPassCounts))
    for i := range passes {
        for j := range jsxPassCounts[i] { passes[i] = append(passes[i], jsxPassCounts[i][j].Load()) }
    }
    return map[string][][]uint64{"cells":cells, "passes":passes}
}
type ObjectLiteralDiscriminator struct {
    jsxAbsent bool
    uncovered int
    cells int""")
call = "discriminated := c.discriminateTypeByDiscriminableItems(contextualType, discriminator)"
edit("internal/checker/jsx.go", call, """discriminator.jsxAbsent = len(discriminantProperties) == 0 && len(discriminantMembers) > 0
    """ + call + """
    if discriminator.jsxAbsent {
        group := 0
        if discriminator.uncovered == 0 { group = 1 }
        jsxPassCounts[group][0].Add(1)
        jsxPassCounts[group][1].Add(uint64(discriminator.cells))
    }""")
site = "targetType := c.getTypeOfPropertyOrIndexSignatureOfType(types[i], discriminator.name(n))"
edit("internal/checker/relater.go",site,"""var prior *Type
                group := 0
                d, observe := discriminator.(*ObjectLiteralDiscriminator)
                if observe && d.jsxAbsent {
                    t := types[i]
                    if t.flags == TypeFlagsIntersection {
                        group = 1
                        if t.objectFlags & (ObjectFlagsIsNeverIntersectionComputed | ObjectFlagsIsNeverIntersection) == ObjectFlagsIsNeverIntersectionComputed &&
                            t.AsIntersectionType().resolvedApparentType == t {
                            group = 2
                            prop := t.AsUnionOrIntersectionType().propertyCacheWithoutFunctionPropertyAugment[discriminator.name(n)]
                            if prop != nil && prop.CheckFlags&ast.CheckFlagsReadPartial == 0 {
                                group = 3
                                if links := c.valueSymbolLinks.TryGet(prop); links != nil && links.resolvedType != nil {
                                    prior = links.resolvedType
                                    group = 4
                                    if prop.CheckFlags&ast.CheckFlagsSyntheticProperty != 0 && links.containingType == t { group = 5
                                    } else if prop.CheckFlags&ast.CheckFlagsInstantiated != 0 { group = 6
                                    } else if prop.CheckFlags&ast.CheckFlagsMapped != 0 { group = 7 }
                                }
                            }
                        }
                    }
                }
                """ + site + """
                if observe && d.jsxAbsent {
                    kind := 0
                    switch {
                    case targetType == nil:
                    case targetType == c.undefinedType: kind = 1
                    case targetType.flags&TypeFlagsUnion != 0 && containsType(targetType.Types(), c.undefinedType): kind = 2
                    case targetType.flags&TypeFlagsStructuredOrInstantiable == 0: kind = 3
                    default: kind = 4
                    }
                    if prior != nil && prior != targetType { kind = 5 }
                    jsxCellCounts[group][kind].Add(1)
                    d.cells++
                    if group != 7 || prior != targetType || (kind != 1 && kind != 2) { d.uncovered++ }
                }""")
path = "cmd/tsgo/main.go"
s = subprocess.check_output(["git","show","21fb142:packages/tsc-go/"+path],cwd=root,text=True)
s = s.replace('"context"', '"context"\n    "encoding/json"\n    "github.com/microsoft/typescript-go/internal/checker"').replace(
    "os.Exit(runMain())", "status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.JsxCellCounts()); os.Exit(status)")
dest = out/"main.go"
dest.write_text(s)
files[str(root/path)] = str(dest)
if "--columns" in sys.argv[2:]:
    checker = out/"checker.go"
    s = checker.read_text().replace("var jsxPassCounts", "var jsxColumns [3][5]atomic.Uint64\nvar jsxPassCounts")
    s = s.replace('return map[string][][]uint64{"cells":cells, "passes":passes}', """columns := make([][]uint64,len(jsxColumns))
    for i := range columns {
        for j := range jsxColumns[i] { columns[i] = append(columns[i], jsxColumns[i][j].Load()) }
    }
    return map[string][][]uint64{"cells":cells, "passes":passes, "columns":columns}""")
    checker.write_text(s)
    relater = out/"relater.go"
    s = relater.read_text()
    start = s.index("func (c *Checker) discriminateTypeByDiscriminableItems(")
    end = s.index("func (c *Checker) filterPrimitivesIfContainsNonPrimitive",start)
    body = s[start:end].replace("matched := false", """matched := false
        var unique map[*ast.Symbol]struct{}
        var activeCells, positive, runs int
        previousPositive := false""")
    body = body.replace("var prior *Type", "var resolvedSymbol *ast.Symbol\n                var prior *Type")
    body = body.replace("prior = links.resolvedType", "prior = links.resolvedType\n                                    resolvedSymbol = prop")
    body = body.replace("d.cells++", """d.cells++
                    activeCells++
                    currentPositive := group == 7 && prior == targetType && (kind == 1 || kind == 2)
                    if currentPositive {
                        positive++
                        if unique == nil { unique = make(map[*ast.Symbol]struct{}) }
                        unique[resolvedSymbol] = struct{}{}
                        if !previousPositive { runs++ }
                    }
                    previousPositive = currentPositive""")
    body = body.replace("// Turn each Ternary.Maybe", """if activeCells != 0 {
            row := 1
            if positive == 0 { row = 0 } else if positive == activeCells { row = 2 }
            for i,v := range [5]int{1, activeCells, positive, len(unique), runs} { jsxColumns[row][i].Add(uint64(v)) }
        }
        // Turn each Ternary.Maybe""")
    relater.write_text(s[:start]+body+s[end:])
if "--neutral" in sys.argv[2:]:
    assert "--columns" in sys.argv[2:]
    checker = out/"checker.go"
    s = checker.read_text().replace("type Checker struct {", """type neutralJsxKey struct {
        target *Type
        member *ast.Symbol
    }
    type Checker struct {
        neutralJsxSeen map[neutralJsxKey]bool""")
    s = s.replace("var jsxColumns", "var jsxNeutral [4][3]atomic.Uint64\nvar jsxColumns")
    s = s.replace('return map[string][][]uint64{"cells":cells, "passes":passes, "columns":columns}', """neutral := make([][]uint64, len(jsxNeutral))
    for i := range neutral {
        for j := range jsxNeutral[i] { neutral[i] = append(neutral[i], jsxNeutral[i][j].Load()) }
    }
    return map[string][][]uint64{"cells":cells,"passes":passes,"columns":columns,"neutral":neutral}""")
    checker.write_text(s)
    relater = out/"relater.go"
    s = relater.read_text()
    site = "if activeCells != 0 {"
    assert s.count(site) == 1
    s = s.replace(site, site + """
            // Retain only observations that covered all original union constituents.
            d := discriminator.(*ObjectLiteralDiscriminator)
            key := neutralJsxKey{target, d.members[n]}
            prior := c.neutralJsxSeen[key]
            all := positive == activeCells
            complete := all && activeCells == len(types)
            bucket := 0
            switch {
            case prior && all: bucket = 1
            case prior: bucket = 2
            case complete: bucket = 3
            }
            if complete && !prior {
                if c.neutralJsxSeen == nil { c.neutralJsxSeen = make(map[neutralJsxKey]bool) }
                c.neutralJsxSeen[key] = true
            }
            jsxNeutral[bucket][0].Add(1)
            jsxNeutral[bucket][1].Add(uint64(activeCells))
            jsxNeutral[bucket][2].Add(uint64(positive))
""")
    relater.write_text(s)
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
