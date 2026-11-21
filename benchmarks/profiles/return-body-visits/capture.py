"""Count return-inference body visits during real checks without changing the answer."""
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
overlay = {str(root / "internal/checker/bodyvisit.go"): str(here / "probe.go.txt")}
def edit(name, changes):
    src = root / name
    data = src.read_text()
    for old, new in changes:
        assert data.count(old) == 1, old
        data = data.replace(old, new)
    dest = out / src.name
    dest.write_text(data)
    overlay[str(src)] = str(dest)

signature = "func (c *Checker) getReturnTypeFromBody(fn *ast.Node, checkMode CheckMode) *Type {"
site = "if contextualSignature != nil && c.getReturnTypeFromAnnotation(node) == nil && signature.resolvedReturnType == nil {\n\t\t\t\treturnType := c.getReturnTypeFromBody(node, checkMode)"
edit("internal/checker/checker.go", [
    ("type Checker struct {", "type Checker struct {\n bodyProbe bodyProbe"),
    (signature, signature + "\n return c.observedBody(fn, checkMode, nil)\n}\n" + signature.replace("getReturnTypeFromBody", "computeObservedBody")),
    (site, site.replace("getReturnTypeFromBody(node, checkMode)", "observedBody(node, checkMode, contextualSignature)")),
])
edit("cmd/tsgo/main.go", [
    ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.BodyVisitReport()); os.Exit(status)"),
])
config = out / "overlay.json"
config.write_text(json.dumps({"Replace": overlay}))
binary = out / "tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay="+str(config), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "projects": {}}
for name, commit, data in observed_projects(binary):
    for group in ("All", "Contextual"):
        for row in data[group]:
            assert row["First"] + row["Repeat"] + row["Reentrant"] == row["Calls"]
            assert row["SameResult"] + row["DifferentResult"] == row["Repeat"]
    assert sum(r["First"] for r in data["All"]) == sum(int(k)*v for k,v in data["CheckerCountPerBody"].items())
    data["commit"] = commit
    report["projects"][name] = data
    print(name, {k:sum(r[k] for r in data["Contextual"]) for k in ("Calls","Repeat")}, flush=True)
    (here / "results.json").write_text(json.dumps(report, indent=2)+"\n")
