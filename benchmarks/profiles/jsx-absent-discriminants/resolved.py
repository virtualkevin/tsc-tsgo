"""Build the per-lookup fast path using only authoritative current checker state."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
files = {}
def edit(file, changes):
    s = subprocess.check_output(["git", "show", "21fb142:packages/tsc-go/"+file], cwd=root, text=True)
    for old,new in changes:
        assert s.count(old) == 1, old
        s = s.replace(old,new)
    dest = out/Path(file).name
    dest.write_text(s)
    files[str(root/file)] = str(dest)
site = "func (c *Checker) discriminateTypeByDiscriminableItems(target *Type, discriminator Discriminator) *Type {"
edit("internal/checker/relater.go", [(site, """// Return true only when the ordinary lookup, symbol resolution and assignability
// check already have a positive answer in the current checker state.
func (c *Checker) resolvedMappedPropertyAcceptsUndefined(t *Type, name string) bool {
    if t.flags != TypeFlagsIntersection || t.objectFlags&(ObjectFlagsMapped|ObjectFlagsIsNeverIntersectionComputed|ObjectFlagsIsNeverIntersection) != ObjectFlagsIsNeverIntersectionComputed {
        return false
    }
    d := t.AsIntersectionType()
    if d.resolvedApparentType != t {
        return false
    }
    prop := d.propertyCacheWithoutFunctionPropertyAugment[name]
    if prop == nil || prop.CheckFlags&(ast.CheckFlagsReadPartial|ast.CheckFlagsDeferredType|ast.CheckFlagsInstantiated|ast.CheckFlagsMapped) != ast.CheckFlagsMapped {
        return false
    }
    links := c.valueSymbolLinks.TryGet(prop)
    if links == nil || links.resolvedType == nil {
        return false
    }
    value := links.resolvedType
    return value == c.undefinedType || (value.flags&TypeFlagsUnion != 0 && containsType(value.Types(), c.undefinedType))
}

""" + site + """
    object, _ := discriminator.(*ObjectLiteralDiscriminator)"""),
("matched := false\n\t\tfor i := range types {", """matched := false
        absent := object != nil && n >= len(object.props)
        for i := range types {"""),
("targetType := c.getTypeOfPropertyOrIndexSignatureOfType(types[i], discriminator.name(n))", """name := discriminator.name(n)
                if absent && c.resolvedMappedPropertyAcceptsUndefined(types[i], name) {
                    matched = true
                    continue
                }
                targetType := c.getTypeOfPropertyOrIndexSignatureOfType(types[i], name)""")])
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
test = root/"internal/checker/jsx_resolved_test.go"
files[str(test)] = str(Path(__file__).resolve().parent/"resolved_test.go.txt")
(out/"test-overlay.json").write_text(json.dumps({"Replace":files}))
