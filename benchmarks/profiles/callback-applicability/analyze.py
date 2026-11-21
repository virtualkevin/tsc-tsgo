"""Partition CPU inside callback checks while checking argument applicability."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
decoder = runpy.run_path(str(here.parent/"call-resolution-partition/analyze.py"))
callback = "checkFunctionExpressionOrObjectLiteralMethod"
context = "contextuallyCheckFunctionExpressionOrObjectLiteralMethod"
body = "getReturnTypeFromBody"
report = {}
for build,folder in [("ordinary","public-native-cpu"),("shipping","shipped-cpu-costs")]:
    base = here.parent/folder
    manifest = json.loads((base/("go.json" if build=="ordinary" else "manifest.json")).read_text())
    data = report[build] = {}
    for project,ref in manifest["projects"].items():
        path = base/(project+("-go.pb.gz" if build=="ordinary" else "-cpu.pb.gz"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == (ref["cpuProfileSha256"] if build=="ordinary" else ref["profiles"]["cpu"])
        raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
        paths, leaves, body_sites = Counter(), Counter(), Counter()
        aggregate = Counter()
        reach_paths = Counter()
        overload_paths = Counter()
        expression_kinds = Counter()
        property_values = Counter()
        all_cpu = 0
        for ns,frames in decoder["decode"](raw):
            all_cpu += ns
            root = [f[0].removeprefix(decoder["PREFIX"]) for f in reversed(frames)]
            # Require the callback to be the argument's expression dispatch.
            path = ["isSignatureApplicable", "checkExpressionWithContextualType", "checkExpressionEx", "checkExpressionWorker", callback]
            owner = next((i for i,n in enumerate(root) if n==callback and i>=len(path)-1 and root[i-len(path)+1:i+1]==path),None)
            if owner is None: continue
            chain = root[owner:]
            def child(i):
                return chain[i+1] if i+1<len(chain) else "(self)"
            phase = child(0)
            if phase==context:
                phase += "/"+child(1)
            paths[phase] += ns
            leaves[chain[-1]] += ns
            if body in chain:
                i=chain.index(body)
                if child(i) == "checkAndAggregateReturnExpressionTypes":
                    walk = chain[i+2:]
                    milestones = ("functionHasImplicitReturn","checkExpressionCachedEx","checkExpressionCached","checkAwaitedType",
                                  "isConstantReference","getMergedSymbol","isReachableFlowNode")
                    step = next((n for n in walk if n in milestones),None)
                    if step=="functionHasImplicitReturn":
                        path = [n for n in walk[walk.index(step)+1:] if n not in ("isReachableFlowNode","isReachableFlowNodeWorker")]
                        if path[:2]==["getEffectsSignature","getResolvedSignature"] and "chooseOverload" in path:
                            j=path.index("chooseOverload")+1
                            if path[j+1:j+4]==["checkExpressionWithContextualType","checkExpressionEx","checkExpressionWorker"]:
                                expression_kinds["/".join([path[j],*path[j+4:j+6]])] += ns
                                if path[j+4:j+7]==["checkObjectLiteral","checkPropertyAssignment","checkExpressionForMutableLocation"]:
                                    rest=path[j+7:]
                                    if rest[:2]==["checkExpressionEx","checkExpressionWorker"]:
                                        rest=rest[2:]
                                    property_values["/".join([path[j],*rest[:3]])] += ns
                            overload_paths["/".join(path[j:j+4])] += ns
                        reach_paths["/".join(path[:5])] += ns
                    aggregate[step or (walk[0] if walk else "(self)")] += ns
                body_sites[f"{frames[len(root)-1-owner-i][2]} {child(i)}"] += ns
        assert paths.total()==leaves.total()
        data[project] = dict(profileSha256=digest,totalNs=all_cpu,callbackNs=paths.total(),directPathNs=dict(paths.most_common()),returnBodySiteNs=dict(body_sites.most_common()),aggregateNs=dict(aggregate.most_common()),reachPathsNs=dict(reach_paths.most_common(25)),overloadPathsNs=dict(overload_paths.most_common(40)),expressionKindsNs=dict(expression_kinds.most_common(30)),propertyValueNs=dict(property_values.most_common(30)),topLeafNs=dict(leaves.most_common(20)))
        print(build,project,paths.total()/1e9,paths.most_common(3),body_sites.most_common(3))
(here/"cpu.json").write_text(json.dumps(report,indent=2)+"\n")
