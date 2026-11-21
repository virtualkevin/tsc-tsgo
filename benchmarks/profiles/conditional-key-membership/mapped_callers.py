"""Find the caller that first entered mapped member resolution in ordinary Go samples."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
shared = runpy.run_path(str(here.parent / "call-resolution-partition/analyze.py"))
old = here.parent / "shipped-cpu-costs"
old_manifest = json.loads((old / "manifest.json").read_text())
current = here.parent / "inherited-member-capacity"
rows = {}
profiles = [(k, old / (k+"-cpu.pb.gz"), v["profiles"]["cpu"]) for k,v in old_manifest["projects"].items()]
profiles.append(("sentry-current", current/"sentry-control-cpu.pb.gz",
                 json.loads((current/"profiles.json").read_text())["binaries"]["control"]["cpu"]))
for name, path, expected in profiles:
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", path], text=True)
    callers = Counter()
    total = 0
    for ns, frames in shared["decode"](raw):
        total += ns
        names = [s.removeprefix(shared["PREFIX"]) for s, _, _ in frames]
        if "resolveMappedTypeMembers" not in names:
            continue
        i = names.index("resolveMappedTypeMembers") + 1
        if i < len(names) and names[i] == "resolveStructuredTypeMembers":
            i += 1
        caller = names[i] if i < len(names) else "(truncated)"
        callers[caller] += ns
    rows[name] = dict(profileSha256=expected, totalCpuNs=total, mappedCpuNs=sum(callers.values()),
                      immediateCallerCpuNs=dict(callers.most_common()))
    print(name, round(100*sum(callers.values())/total,2), callers.most_common(3))
(here / "mapped-callers.json").write_text(json.dumps(rows, indent=2)+"\n")
