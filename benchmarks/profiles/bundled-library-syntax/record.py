"""Record median kernel times and allocation costs from three Go benchmark samples."""
from pathlib import Path
import re
from statistics import median
import sys

here = Path(__file__).resolve().parent
raw = Path(sys.argv[1]).read_text()
assert "PASS" in raw.splitlines()
for library in ("lib.dom.d.ts", "lib.es5.d.ts"):
    def samples(mode):
        pattern = rf"^BenchmarkLibraryFrontEnd/{re.escape(library)}/{mode}-\d+\s+\d+\s+(\d+) ns/op\s+(\d+) B/op\s+(\d+) allocs/op$"
        measurements = re.findall(pattern, raw, re.MULTILINE)
        assert len(measurements) == 3, (library, mode, measurements)
        return tuple(median(int(sample[i]) for sample in measurements) for i in range(3))

    parse, decode = samples("parse"), samples("decode")
    row = (f"| Decode bundled library API syntax (in memory) | {library} | Go parser | "
           f"{parse[0]/1e6:.3f} | {decode[0]/1e6:.3f} | {parse[0]/decode[0]:.3f}× | 3 | "
           f"{parse[1]:,} vs {decode[1]:,} B/op. Decoder omits parser metadata. "
           "[Samples](benchmarks/profiles/bundled-library-syntax/bench.txt) |")
    table = here.parents[2] / "PERF.md"
    assert row not in table.read_text()
    with table.open("a") as f:
        f.write(row + "\n")
    print(row)
(here / "bench.txt").write_text(raw)
