"""Build and test the full-key-union construction candidate."""
import json
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
go = sys.argv[2]
checker = root / "internal/checker/checker.go"
site = "result := c.getUnionTypeEx(types, UnionReductionLiteral, nil, origin)\n\tc.propertiesTypes[key] = result"
source = checker.read_text()
assert source.count(site) == 1
modified = out / "checker.go"
modified.write_text(source.replace(site, "result := c.unionOfPropertyKeys(types, origin)\n\tc.propertiesTypes[key] = result"))
files = {str(checker): str(modified), str(checker.parent / "property_keys.go"): str(here / "keys.go.txt")}
cfg = out / "overlay.json"
cfg.write_text(json.dumps({"Replace": files}))
subprocess.run([go, "build", "-buildvcs=false", "-overlay=" + str(cfg), "-o", out / "tsgo", "./cmd/tsgo"], cwd=root, check=True)
files[str(checker.parent / "property_keys_test.go")] = str(here / "keys_test.go.txt")
cfg = out / "test-overlay.json"
cfg.write_text(json.dumps({"Replace": files}))
subprocess.run([go, "test", "-overlay=" + str(cfg), "-count=1", "./internal/checker", "./internal/compiler", "./internal/execute"], cwd=root, check=True)
