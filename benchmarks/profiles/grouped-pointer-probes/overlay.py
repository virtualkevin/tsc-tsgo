"""Layer grouped probing onto either the stock or the size-aware compiler."""
import json
from pathlib import Path
import sys

out = Path(sys.argv[1]).resolve()
root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out.mkdir(exist_ok=True)
source = root / "internal/core/pointerlinkstore.go"
before = source.read_text()
start = before.index("\tfor range len(s.entries) {")
end = before.index('\tpanic("PointerLinkStore has no empty slot")', start)
replacement = '''\t// Visit each four-slot group once. Triangular group offsets permute a
\t// power-of-two group count, including when the first group wraps.
\tfor step := 4; step <= len(s.entries); step += 4 {
\t\tfor offset := range 4 {
\t\t\tslot := (index + offset) & mask
\t\t\tentry := &s.entries[slot]
\t\t\tif entry.value == nil || entry.key == key {
\t\t\t\treturn slot
\t\t\t}
\t\t}
\t\tindex = (index + step) & mask
\t}
'''
updated = out / source.name
updated.write_text(before[:start] + replacement + before[end:])
overlay = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {"Replace":{}}
overlay["Replace"][str(source)] = str(updated)
(out / "overlay.json").write_text(json.dumps(overlay))
