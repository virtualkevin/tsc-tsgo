"""Exercise the new ordered path and its fallback against the original algorithm."""
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
config = json.loads((out / "overlay.json").read_text())
source = (here.parent / "reduction-small-pair/reduction_small_pair_test.go").read_text()
# Zero padding keeps the width-16 and width-256 cases in lexical order.
source = source.replace('fmt.Sprintf("p%d", i)', 'fmt.Sprintf("p%03d", i)')
source = source.replace('"p0"', '"p000"').replace('8, 9, 16}', '8, 9, 16, 256}')
# Put the conflict last to exercise a long run of missing or matching names.
source = source.replace('lazyProperty(c, "p000", b, optional)',
                        'lazyProperty(c, fmt.Sprintf("p%03d", width-1), b, optional)')
dest = out / "ordered_pair_test.go"
source += (here / "bench.go.txt").read_text()
if len(sys.argv) > 2 and sys.argv[2] == "layout":
    source += (here / "layout_test.go.txt").read_text()
dest.write_text(source)
config["Replace"][str(root / "internal/checker/ordered_pair_test.go")] = str(dest)
(out / "test-overlay.json").write_text(json.dumps(config))
