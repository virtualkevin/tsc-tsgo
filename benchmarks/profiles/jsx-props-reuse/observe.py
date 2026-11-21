"""Measure repeated JSX props computations by syntax node and signature on each checker."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
module = here.parents[2] / "packages/tsc-go"
scratch = Path(sys.argv[1]).resolve()
scratch.mkdir(parents=True, exist_ok=True)
overlay = {str(module / "internal/checker/props_probe.go"): str(here / "probe.go.txt")}
for name, changes in {
    "internal/checker/checker.go": [("type Checker struct {", "type Checker struct {\n propsProbe propsProbe")],
    "internal/checker/jsx.go": [("func (c *Checker) getEffectiveFirstArgumentForJsxSignature(", "func (c *Checker) computeEffectiveJsxProps(")],
    "cmd/tsgo/main.go": [('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
                         ("os.Exit(runMain())", "status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.PropsReport()); os.Exit(status)")],
}.items():
    path = module / name
    source = path.read_text()
    for old, new in changes:
        assert source.count(old) == 1
        source = source.replace(old, new)
    dest = scratch / path.name
    dest.write_text(source)
    overlay[str(path)] = str(dest)

config = scratch / "overlay.json"
config.write_text(json.dumps({"Replace": overlay}))
binary = scratch / "tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay="+str(config), "-o", binary, "./cmd/tsgo"], cwd=module, check=True)
ref = json.loads(gzip.decompress((here.parent / "named-key-union/public.json.gz").read_bytes()))
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "SCRIPTC_", "TS_GO_", "GODEBUG", "GOMAXPROCS", "GOGC", "GOMEMLIMIT"))}
env.update(ref["environment"]["compilerEnvironment"])
project = next(p for p in ref["projects"] if p["name"] == "sentry")
cwd = Path(project["cwd"])
assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd, text=True).strip() == project["commit"]
inputs = project["preflight"]["candidate"]["inputs"]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
assert all(sha(cwd / i["file"]) == i["sha256"] for i in inputs)
args = project["compilerArgs"]["candidate"]
run = subprocess.run([binary,*args], cwd=cwd, env=env, capture_output=True, text=True, check=True, timeout=480)
assert not run.stdout
workers = json.loads(run.stderr)
assert workers and all(w["Calls"] >= w["Repeat"] >= w["Changed"] for w in workers)
totals = {k:sum(w[k] for w in workers) for k in workers[0]}
print(totals)
(here / "sentry.json").write_text(json.dumps(dict(commit=project["commit"], files=len(inputs), args=args, binarySha256=sha(binary), workers=workers, totals=totals), indent=2)+"\n")
