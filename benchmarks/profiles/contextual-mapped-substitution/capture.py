"""Count checker-local repeated contextual mapped substitutions, executing every request."""
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
files = {str(root / "internal/checker/substitution_demand.go"): str(here / "probe.go.txt")}
for file, edits in [
    ("internal/checker/checker.go", [
        ("type Checker struct {", "type Checker struct {\n substitutionDemand *substitutionDemand"),
        ("return c.substituteIndexedMappedType(t, propertyNameType)", "return c.observeContextualMappedSubstitution(t, propertyNameType)")]),
    ("cmd/tsgo/main.go", [
        ('"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
        ("os.Exit(runMain())", "status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.SubstitutionDemand()); os.Exit(status)")])
]:
    path = root / file
    src = path.read_text()
    for old, new in edits:
        assert src.count(old) == 1, old
        src = src.replace(old, new)
    dest = out / path.name
    dest.write_text(src)
    files[str(path)] = str(dest)
overlay = out / "overlay.json"
overlay.write_text(json.dumps({"Replace": files}))
binary = out / "tsgo"
subprocess.run([sys.argv[2], "build", "-buildvcs=false", "-overlay=" + str(overlay), "-o", binary, "./cmd/tsgo"], cwd=root, check=True)
r = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
     "rows": ["no resident match", "repeated object/index and identical result", "repeated object/index and different result"],
     "columns": ["outer calls", "descendant instantiations", "calls with instantiation", "calls changing current instantiation budget"], "projects": {}}
for name, commit, counts in observed_projects(binary):
    assert len(counts) == 3 and all(len(row) == 4 and row[0] >= max(row[2:]) and row[1] >= row[2] for row in counts)
    r["projects"][name] = {"commit": commit, "counts": counts}
    print(name, counts, flush=True)
(here / "counts.json").write_text(json.dumps(r, indent=2) + "\n")
