"""Count direct non-naked intersection-member visits on unchanged true-branch slices."""
import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

def sparse(rows):
    return {f"{index},{mask}": count for index, row in enumerate(rows)
            for mask, count in enumerate(row) if count}

binary = Path(sys.argv[1]).resolve()
report = {
    "binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    "bits": ["immediateGuard", "visitedHit", "visitedInsert", "definitelyUnrelated",
             "inferFromProperties", "variablePriority"],
    "synthetic64": sparse(json.loads(Path(sys.argv[2]).read_text())),
    "projects": {},
}
for name, commit, rows in observed_projects(binary):
    report["projects"][name] = {"commit": commit, "counts": sparse(rows)}
    print(name, sparse(rows), flush=True)
(here / "counts.json").write_text(json.dumps(report, indent=2) + "\n")
