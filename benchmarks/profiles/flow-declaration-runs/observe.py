"""Count fresh declaration comparisons and lengths of reused declaration runs."""
from pathlib import Path
import json
import subprocess
import sys

here = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
subprocess.run([sys.executable,here/"prepare.py",out],check=True)
p = out/"flow.go"
s = p.read_text().replace("import (",'import (\n "sync/atomic"')
s = s.replace("type declarationRun struct {","type declarationRun struct {\n length uint64")
s = s.replace("previous := c.declarationRun","var scanned, inherited uint64\n previous := c.declarationRun")
s = s.replace("next = previous.next", "inherited = previous.length\n next = previous.next")
s = s.replace("next = next.Antecedent\n    }","scanned++\n next = next.Antecedent\n    }")
s = s.replace("c.declarationRun = declarationRun{base, first, next}", """flowRunCounts[0].Add(1)
        flowRunCounts[1].Add(scanned)
        if inherited != 0 { flowRunCounts[2].Add(1); flowRunCounts[3].Add(inherited) }
        c.declarationRun = declarationRun{scanned+inherited, base, first, next}""")
s += """
var flowRunCounts [4]atomic.Uint64
func ObservedFlowRuns() (out [4]uint64) {
    for i := range out { out[i]=flowRunCounts[i].Load() }
    return out
}
"""
p.write_text(s)
root = here.parents[2]/"packages/tsc-go"
name = "cmd/tsgo/main.go"
s = subprocess.check_output(["git","show","78dd830:packages/tsc-go/"+name],cwd=root,text=True)
s=s.replace('"context"', '"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
s=s.replace("os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.ObservedFlowRuns()); os.Exit(status)")
(out/"main.go").write_text(s)
p=out/"overlay.json"
contents=json.loads(p.read_text())
contents["Replace"][str(root/name)] = str(out/"main.go")
p.write_text(json.dumps(contents))
