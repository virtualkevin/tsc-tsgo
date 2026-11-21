"""Count merge shapes and input sizes in the experimental sorted-run compiler."""
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[3]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True)
checker=root/"internal/checker/checker.go"
main=root/"cmd/tsgo/main.go"
s=checker.read_text()
site="func mergeStringLiteralRun(set, run []*Type) []*Type {"
assert s.count(site)==1
s=s.replace(site,"""var mergeCounts [9]atomic.Uint64
func MergeCounts() []uint64 {
    values := make([]uint64,len(mergeCounts))
    for i := range values { values[i] = mergeCounts[i].Load() }
    return values
}
"""+site+"""
    mergeCounts[0].Add(1)
    mergeCounts[1].Add(uint64(len(set)))
    mergeCounts[2].Add(uint64(len(run)))
    if len(run) >= 1024 { mergeCounts[8].Add(1) }
""")
for old,new in [
    ("if start == len(set) {\n\t\treturn append(set, run...)","if start == len(set) {\n mergeCounts[3].Add(1); return append(set, run...)"),
    ("if start == end {\n\t\treturn slices.Insert(set, start, run...)","if start == end {\n mergeCounts[4].Add(1); return slices.Insert(set, start, run...)"),
    ("if slices.Equal(existing, run) {\n\t\treturn set","if slices.Equal(existing, run) {\n mergeCounts[5].Add(1); return set"),
    ("merged := make([]*Type, 0, len(existing)+len(run))","mergeCounts[6].Add(1); mergeCounts[7].Add(uint64(len(existing))); merged := make([]*Type, 0, len(existing)+len(run))"),
]:
    assert s.count(old)==1
    s=s.replace(old,new)
(out/checker.name).write_text(s)
s=main.read_text().replace('"context"', '"context"\n "fmt"\n "github.com/microsoft/typescript-go/internal/checker"')
s=s.replace("os.Exit(runMain())","status := runMain(); fmt.Fprintln(os.Stderr,checker.MergeCounts()); os.Exit(status)")
(out/main.name).write_text(s)
(out/"overlay.json").write_text(json.dumps({"Replace":{str(p):str(out/p.name) for p in (checker,main)}}))
