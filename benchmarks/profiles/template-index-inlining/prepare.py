"""Isolate the numeric-string fallback to keep the ordinary index query inlineable."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
path = Path("packages/tsc-go/internal/checker/checker.go")
source = subprocess.check_output(["git","show", f"a6444de:{path}"], cwd=root, text=True)
marker = "func (c *Checker) isApplicableIndexType(source *Type, target *Type) bool {"
end = source.index("\n}", source.index(marker)) + 2
start = source.index(marker)
old = source[start:end]
numeric = "target == c.numberType && (source == c.numericStringType || source.flags&TypeFlagsStringLiteral != 0 && isNumericLiteralName(getStringLiteralValue(source)))"
assert old.count(numeric) == 1
source = source[:start] + old.replace(numeric, "target == c.numberType && c.isNumericIndexKey(source)") + """

// Keep numeric string parsing off the common string and template index paths.
//go:noinline
func (c *Checker) isNumericIndexKey(source *Type) bool {
	return source == c.numericStringType || source.flags&TypeFlagsStringLiteral != 0 && isNumericLiteralName(getStringLiteralValue(source))
}
""" + source[end:]
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True, parents=True)
staged = out / path.name
staged.write_text(source)
(out/"overlay.json").write_text(json.dumps({"Replace": {str(root/path): str(staged)}}))
