"""Compare a cached body type with the actual deferred expression check in place."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = {str(root/"internal/checker/deferredprobe.go"): str(here/"deferred.go.txt")}
def edit(name, changes):
    path = root/name
    data = path.read_text()
    for old, new in changes:
        assert data.count(old) == 1, old
        data = data.replace(old, new)
    dest = out/path.name
    dest.write_text(data)
    overlay[str(path)] = str(dest)

edit("internal/checker/checker.go", [
    ("type Checker struct {", "type Checker struct {\n deferredProbe deferredRows"),
    ("exprType := c.checkExpression(body)", "exprType := c.observeDeferredBody(body)"),
    ("c.diagnostics.Add(diagnostic)", "c.deferredProbe.adds++; c.diagnostics.Add(diagnostic)"),
])
edit("cmd/tsgo/main.go", [
    ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.DeferredReport()); os.Exit(status)"),
])
config = out/"overlay.json"
config.write_text(json.dumps({"Replace":overlay}))
binary = out/"tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay="+str(config), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "projects": {}}
for name, commit, data in observed_projects(binary):
    assert data and all(row["Calls"] >= row["Changed"] for row in data.values())
    report["projects"][name] = dict(commit=commit, groups=data)
    (here/"deferred.json").write_text(json.dumps(report,indent=2)+"\n")
    print(name, data, flush=True)
