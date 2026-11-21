"""Instrument the grouped candidate to count reused spans and invalidations."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
subprocess.run([sys.executable, here/"watched.py", out],check=True)
overlay = out/"overlay.json"
files = json.loads(overlay.read_text())["Replace"]
path=out/"watched_groups.go"
s=path.read_text().replace('"slices"', '"slices"\n"sync/atomic"')
s += """
var jsxPlanCounts [7]atomic.Uint64
func JsxPlanCounts() (out [7]uint64) {
    for i:= range out { out[i]=jsxPlanCounts[i].Load() }
    return out
}
"""
def add(text,site,replacement):
    assert text.count(site)==1,site
    return text.replace(site,replacement)

s=add(s,"if links.watchesAbsentProperties && links.resolvedType != value {", "if links.watchesAbsentProperties && links.resolvedType != value {\n        jsxPlanCounts[0].Add(1)")
s=add(s,"if previous := cache[name]; previous != nil && previous != prop {", "if previous := cache[name]; previous != nil && previous != prop {\n        jsxPlanCounts[1].Add(1)")
s=add(s,"plan := &absentPropertyPlan{", "jsxPlanCounts[2].Add(1)\n    plan := &absentPropertyPlan{")
path.write_text(s)
path=out/"relater.go"
s=add(path.read_text(),"if c.validLinkedSpan(target, plan, span) {","""jsxPlanCounts[3].Add(1)
            if c.validLinkedSpan(target, plan, span) {
                jsxPlanCounts[4].Add(1)
                jsxPlanCounts[5].Add(uint64(span.end-span.start))
                enabled := 0
                for _, v := range include { if v != TernaryFalse { enabled++ } }
                jsxPlanCounts[6].Add(uint64(enabled*(span.end-span.start)))""")
path.write_text(s)
path=root/"cmd/tsgo/main.go"
s=path.read_text()
s=add(s,'"context"','"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
s=add(s,"os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.JsxPlanCounts()); os.Exit(status)")
dest=out/"main.go"
dest.write_text(s)
files[str(path)]=str(dest)
overlay.write_text(json.dumps({"Replace":files}))
