"""Compare flat allocated bytes at both table allocation sites and whole-run totals."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
manifest = json.loads((here / "profiles.json").read_text())
report = {}
for role, profile in manifest["binaries"].items():
    path = here / f"sentry-{role}-mem.pb.gz"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == profile["mem"]
    top = subprocess.check_output([sys.argv[1], "tool", "pprof", "-top", "-sample_index=alloc_space",
                                   "-unit=bytes", "-nodecount=0", "-nodefraction=0", path], text=True)
    total = int(re.search(r"100% of (\d+)B total", top)[1])
    allocations = {}
    for method in ("(*Checker).addInheritedMembers", "(*pendingInstantiatedMembers).ownTable"):
        lines = [line for line in top.splitlines() if line.endswith("internal/checker." + method)]
        assert len(lines) == 1, lines
        allocations[method] = int(lines[0].split()[0].removesuffix("B"))
    report[role] = {"totalAllocatedBytes": total, "flatAllocatedBytes": allocations,
                    "combinedFlatBytes": sum(allocations.values())}
(here / "allocation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
