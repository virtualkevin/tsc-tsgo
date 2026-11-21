"""Build the finite-string relation shortcut against the current index-key helper."""
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
relater = root / "internal/checker/relater.go"
source = relater.read_text()
site = "if source == target {\n\t\treturn true\n\t}\n\tif relation != c.identityRelation {"
assert source.count(site) == 1
guard = """if source == target {
		return true
	}
	// A finite literal matching a template must contain both fixed ends.
	if source.flags&TypeFlagsStringLiteral != 0 && target.flags&TypeFlagsTemplateLiteral != 0 &&
		unmatchedTemplateIndexKey(source, target.AsTemplateLiteralType()) {
		return false
	}
	if relation != c.identityRelation {"""
dest = out / "relater.go"
dest.write_text(source.replace(site, guard))
files = {str(relater): str(dest)}
(out / "overlay.json").write_text(json.dumps({"Replace": files}))

draft = here.parent / "template-entry-guard-draft/string-template-entry-guard.patch"
for block in draft.read_text().split("--- /dev/null\n")[1:]:
    header, hunk, *lines = block.splitlines()
    file = Path(header.split("/")[-1])
    assert file.name.endswith("_test.go") and hunk.startswith("@@ -0,0")
    assert all(s.startswith("+") for s in lines)
    src = "\n".join(s[1:] for s in lines) + "\n"
    src = src.replace("relation.size()", "len(relation.results)")
    src = src.replace("c.strictNullChecks = true", """c.strictNullChecks = true
	c.globalStringType = c.newObjectType(ObjectFlagsAnonymous, nil)
	c.unknownType = c.newIntrinsicType(TypeFlagsUnknown, "unknown")
	c.couldContainTypeVariables = c.couldContainTypeVariablesWorker""")
    test_file = out / file.name
    test_file.write_text(src)
    files[str(relater.parent / file.name)] = str(test_file)
(out / "test-overlay.json").write_text(json.dumps({"Replace": files}))
