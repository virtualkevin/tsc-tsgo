"""Partition CPU under the innermost synthesized union/intersection property."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
base = here.parent/"shipped-cpu-costs"
manifest = json.loads((base/"manifest.json").read_text())
shared = runpy.run_path(str(here.parent/"call-resolution-partition/analyze.py"))
report = {}
for project, info in manifest["projects"].items():
    path = base/f"{project}-cpu.pb.gz"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == info["profiles"]["cpu"]
    raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
    total = 0
    apparent = Counter()
    descendants = Counter()
    apparent_callers = Counter()
    callers, work, reads = Counter(), Counter(), Counter()
    for ns, frames in shared["decode"](raw):
        total += ns
        names = [f[0].removeprefix(shared["PREFIX"]) for f in frames]
        if "getReducedApparentType" in names:
            j = names.index("getReducedApparentType")
            direct = all(name in {"getReducedType","getApparentType"} for name in names[:j])
            apparent["selfOrDirectHelperLeaf" if direct else "deeperCallees"] += ns
            if not direct:
                first = next(n for n in reversed(names[:j]) if n not in {"getReducedType","getApparentType"})
                descendants[first] += ns
            if direct:
                apparent_callers[names[j+1] if len(names)>j+1 else "(root)"] += ns
        if "createUnionOrIntersectionProperty" not in names:
            continue
        i = names.index("createUnionOrIntersectionProperty")
        caller = next((name for name in names[i+1:] if name not in
                       {"getUnionOrIntersectionProperty","getPropertyOfUnionOrIntersectionType"}),"(root)")
        callers[caller] += ns
        child = names[i-1] if i else "(self)"
        work[child] += ns
        if child == "getPropertyOfTypeEx":
            reads[names[i-2] if i>=2 else "(self)"] += ns
    assert sum(callers.values()) == sum(work.values()) <= total
    report[project] = dict(profileSha256=digest,totalCpuNs=total,constructNs=sum(work.values()),
                           byCallerNs=callers,byChildNs=work,constituentPropertyChildrenNs=reads,
                           reducedApparentNs=apparent,directApparentCallerNs=apparent_callers,apparentDescendantsNs=descendants)
out=json.dumps(report,indent=2,sort_keys=True)+"\n"
if "--write" in sys.argv:
    (here/"cpu.json").write_text(out)
else:
    assert (here/"cpu.json").read_text()==out
