import hashlib
import json
import os
import subprocess
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
          "columns": ["calls", "nestedPropertyOrIndexQueries", "changedResultOnRepeat", "narrowed",
                      "callsWithInstantiations", "callsCreatingTypes", "callsCreatingSymbols",
                      "callsChangingAssignableSize", "callsChangingSubtypeSize", "callsUnderActiveInstantiation"],
          "projects": {}}
groups = ["explicit", "empty", "firstAbsent", "changedAbsentNames", "repeatAbsentNames"]
env = {k: v for k, v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env["TSC_TS_LIB_DIR"] = str(here.parents[2] / "upstream/typescript-go/internal/bundled/libs")
result = subprocess.run([binary, "--ignoreConfig", "--strict", "--skipLibCheck", "--jsx", "preserve",
                         "--noEmit", "probe.tsx"], cwd=here, env=env, capture_output=True, text=True, check=True)
assert not result.stdout
fixture = json.loads(result.stderr)
assert all(len(row) == len(report["columns"]) for row in fixture)
assert [row[:3] for row in fixture] == [[1, 2, 0], [0, 0, 0], [1, 2, 0], [0, 0, 0], [2, 4, 0]]
report["fixture"] = dict(zip(groups, fixture, strict=True))
for name, commit, rows in observed_projects(binary, projects={"sentry"}):
    report["projects"][name] = {"commit": commit, "groups": dict(zip(groups, rows, strict=True))}
(here / "counts.json").write_text(json.dumps(report, indent=2) + "\n")
print(report)
