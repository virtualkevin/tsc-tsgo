"""Track deferred callback signatures through the first subsequent body inference."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
overlay = {str(root/"internal/checker/void_probe.go"): str(here/"probe.go.txt")}
def edit(name, changes):
    path = root/name
    source = path.read_text()
    for old,new in changes:
        assert source.count(old) == 1, old
        source = source.replace(old,new)
    dest = out/path.name
    dest.write_text(source)
    overlay[str(path)] = str(dest)

site = "if contextualSignature != nil && c.getReturnTypeFromAnnotation(node) == nil && signature.resolvedReturnType == nil {"
edit("internal/checker/checker.go", [
    ("type Checker struct {", "type Checker struct {\n voidProbe voidCallbackProbe"),
    (site, site[:-1] + "&& !c.recordVoidDeferral(contextualSignature, signature) {"),
    ("t = c.getReturnTypeFromBody(sig.declaration, CheckModeNormal)", "t = c.observeReturnDemand(sig)"),
    ("c.getReturnTypeOfSignature(c.getSignatureFromDeclaration(node))\n\t\t}\n\t\tif ast.IsBlock(body)",
     "c.observeDeferredCheck(c.getSignatureFromDeclaration(node))\n\t\t}\n\t\tif ast.IsBlock(body)"),
])
edit("cmd/tsgo/main.go", [
    ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.VoidDeferrals()); os.Exit(status)"),
])
config = out/"overlay.json"
config.write_text(json.dumps({"Replace":overlay}))
binary = out/"tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay="+str(config), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(), "projects":{}}
for name, commit, data in observed_projects(binary):
    for row in data:
        assert row["New"] == row["Outstanding"] + row["DeferredCheck"] + row["OtherDemand"]
    report["projects"][name] = dict(commit=commit, workers=data)
    print(name, {k:sum(r[k] for r in data) for k in data[0]}, flush=True)
    (here/"demand.json").write_text(json.dumps(report,indent=2)+"\n")
