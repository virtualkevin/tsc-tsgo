"""Generate a scanner and binder overlay from the compiler's keyword definitions."""
import json
from pathlib import Path
import re
import sys

src = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
scanner = src / "internal/scanner/scanner.go"
binder = src / "internal/binder/binder.go"
source = scanner.read_text()
table = source.split("var textToKeyword = map[string]ast.Kind{", 1)[1].split("\n}", 1)[0]
keywords = re.findall(r'"([^"]+)":\s+ast\.(\w+),', table)
assert len(keywords) == table.count(":")
kinds = (src / "internal/ast/kind_generated.go").read_text()
first, last = (re.search(r"Kind" + name + r"FutureReservedWord\s*= (\w+)", kinds)[1]
               for name in ("First", "Last"))
ordered = re.findall(r"^\s*(Kind\w+Keyword)\s*$", kinds, re.M)
reserved = set(ordered[ordered.index(first):ordered.index(last) + 1]) | {"KindAwaitKeyword"}
assert len(reserved) == 10
def classify(name, pairs):
    lines = [f"func {name}(str string) ast.Kind {{", "\tswitch str {"]
    for word, kind in pairs:
        lines.extend([f'\tcase "{word}":', f"\t\treturn ast.{kind}"])
    return "\n".join(lines + ["\t}", "\treturn ast.KindIdentifier", "}"])

before = re.search(r"func GetIdentifierToken\(str string\) ast.Kind \{.*?\n}", source, re.S)[0]
(out / "scanner.go").write_text(source.replace(before, classify("GetIdentifierToken", keywords)))
source = binder.read_text()
anchor = "func (b *Binder) checkContextualIdentifier(node *ast.Node) {"
start = "\t\toriginalKeywordKind := scanner.GetIdentifierToken(node.Text())\n\t\tif originalKeywordKind == ast.KindIdentifier {\n\t\t\treturn\n\t\t}\n"
assert source.count(anchor) == source.count(start) == 1
classifier = classify("contextualDiagnosticKeyword", [(w,k) for w,k in keywords if k in reserved])
guard = "\n\toriginalKeywordKind := contextualDiagnosticKeyword(node.AsIdentifier().Text)\n\tif originalKeywordKind == ast.KindIdentifier {\n\t\treturn\n\t}"
(out / "binder.go").write_text(source.replace(start, "").replace(anchor, classifier + "\n\n" + anchor + guard))
(out / "overlay.json").write_text(json.dumps({"Replace": {
    str(scanner): str(out / "scanner.go"),
    str(binder): str(out / "binder.go"),
    str(binder.with_name("keyword_dispatch_test.go")): str(Path(__file__).with_name("classify_test.go.txt").resolve()),
}}))
