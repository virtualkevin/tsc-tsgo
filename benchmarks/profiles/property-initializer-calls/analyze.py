"""Compare nested call resolution in property initializers with all call expressions."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
decoder = runpy.run_path(str(here.parent/"call-resolution-partition/analyze.py"))
initializer = ["checkPropertyAssignment", "checkExpressionForMutableLocation", "checkExpressionEx",
               "checkExpressionWorker", "checkCallExpression", "getResolvedSignature", "resolveSignature", "resolveCallExpression"]
report = {}
for build, folder, manifest in [("ordinary", "public-native-cpu", "go.json"), ("shipping", "shipped-cpu-costs", "manifest.json")]:
    projects = report[build] = {}
    for project, ref in json.loads((here.parent/folder/manifest).read_text())["projects"].items():
        filename = project + ("-go.pb.gz" if build=="ordinary" else "-cpu.pb.gz")
        path = here.parent/folder/filename
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha == (ref["cpuProfileSha256"] if build=="ordinary" else ref["profiles"]["cpu"])
        raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
        branches = {scope: Counter() for scope in ("initializer","all")}
        detail = {scope: Counter() for scope in branches}
        total = 0
        for ns, frames in decoder["decode"](raw):
            total += ns
            names = [f[0].removeprefix(decoder["PREFIX"]) for f in reversed(frames)]
            # Pick the outermost matching resolution separately in each scope.
            for scope in branches:
                i = next((i for i,n in enumerate(names) if n=="resolveCallExpression" and
                          (scope=="all" or names[max(0,i-len(initializer)+1):i+1]==initializer)), None)
                if i is None: continue
                rest = names[i+1:]
                step = rest[0] if rest else "(self)"
                branches[scope][step] += ns
                if step=="resolveCall" and "chooseOverload" in rest:
                    j = rest.index("chooseOverload")
                    key = "/".join(rest[j:j+5])
                else:
                    key = "/".join(rest[:6]) or "(self)"
                detail[scope][key] += ns
        assert all(branches[s].total()==detail[s].total() for s in branches)
        projects[project] = dict(profileSha256=sha,totalNs=total,scopes={
            s:dict(ns=branches[s].total(),branches=dict(branches[s].most_common()),paths=dict(detail[s].most_common(20))) for s in branches})
        print(build,project,[(s,round(branches[s].total()/1e9,2),[(n,round(v/1e9,2)) for n,v in branches[s].most_common(2)]) for s in branches])
(here/"cpu.json").write_text(json.dumps(report,indent=2)+"\n")
