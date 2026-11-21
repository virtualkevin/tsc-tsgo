"""Compare the reduced handler fixture's flow cost with the four pinned projects."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
shipped = here.parent / "shipped-cpu-costs"
manifest = json.loads((shipped / "manifest.json").read_text())
functions = ("getTypeAtFlowAssignment", "isMatchingReference", "getTypeAtFlowNode", "getTypeOfInstantiatedSymbol")
report = {}
for name in ("vscode", "sentry", "typeorm", "trpc","handlers4096"):
    profile = shipped / f"{name}-cpu.pb.gz"
    if name == "handlers4096":
        profile = here / "handlers4096-cpu.pb.gz"
        expected = "28b5fb67497f46f065f0f39fe391b2ec2e8132d0f131005a662048351c423510"
    else:
        expected = manifest["projects"][name]["profiles"]["cpu"]
    if name == "sentry":
        profile = here.parent / "template-index-text/sentry-guard.pb.gz"
        expected = (profile.parent / "profile-sha256.txt").read_text().split()[1]
    assert hashlib.sha256(profile.read_bytes()).hexdigest() == expected
    out = subprocess.check_output([sys.argv[1], "tool", "pprof", "-top", "-nodefraction=0",
                                  "-nodecount=0", "-unit=ms", profile], text=True)
    table = {}
    for fn in functions:
        lines = [line for line in out.splitlines()
                 if re.search(r"internal/checker\.\(\*Checker\)\." + fn + r"(?: \(inline\))?$", line)]
        assert len(lines) <= 1
        table[fn] = float(lines[0].split()[4].rstrip("%")) if lines else 0
    assert table["getTypeOfInstantiatedSymbol"] > 0
    report[name] = {"profileSha256": expected, "inclusiveCpuPercent": table}
    print(name, table)
(here/"flow.json").write_text(json.dumps(report, indent=2)+"\n")
