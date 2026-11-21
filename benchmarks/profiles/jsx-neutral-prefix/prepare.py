"""Specialize only the JSX call site, leaving the ordinary discriminator intact."""
from pathlib import Path
import json
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go/internal/checker"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
jsx = root / "jsx.go"
site = "discriminated := c.discriminateTypeByDiscriminableItems(contextualType, discriminator)"
s = jsx.read_text()
assert s.count(site) == 1
(out / "jsx.go").write_text(s.replace(site, """var discriminated *Type
	if len(discriminantProperties) == 0 && len(discriminantMembers) >= 8 && len(contextualType.Types()) <= 16 {
		discriminated = c.discriminateAbsentMembers(contextualType, discriminator)
	} else {
		discriminated = c.discriminateTypeByDiscriminableItems(contextualType, discriminator)
	}"""))
s = (root / "relater.go").read_text()
a = s.index("func (c *Checker) discriminateTypeByDiscriminableItems(")
b = s.index("\nfunc ", a + 1)
worker = s[a:b].replace("discriminateTypeByDiscriminableItems(target *Type, discriminator Discriminator)", "discriminateAbsentMembers(target *Type, discriminator *ObjectLiteralDiscriminator)")
site = "for n := range discriminator.len() {"
assert worker.count(site) == 1
worker = worker.replace(site, """for n := 0; n < len(discriminator.members); n++ {
		n += c.neutralAbsentPrefix(types, include, discriminator.members[n:])
		if n == len(discriminator.members) {
			break
		}""")
if "--bounded" in sys.argv[2:]:
    site = "n += c.neutralAbsentPrefix(types, include, discriminator.members[n:])"
    assert worker.count(site) == 1
    worker = worker.replace(site, """end := n + min(16, len(discriminator.members)-n)
        n += c.neutralAbsentPrefix(types, include, discriminator.members[n:end])
        if n == end {
            n--
            continue
        }""")
code = (here / "prefix.go.txt").read_text().replace("import ", 'import "slices"\n\nimport ', 1)
(out / "prefix.go").write_text(code + "\n" + worker)
overlay = {str(jsx): str(out / "jsx.go"), str(root / "neutral_absent_prefix.go"): str(out / "prefix.go")}
(out / "overlay.json").write_text(json.dumps({"Replace": overlay}))
overlay[str(root / "neutral_absent_prefix_test.go")] = str(here / "prefix_test.go.txt")
(out / "test-overlay.json").write_text(json.dumps({"Replace": overlay}))
