"""Find first-pass work in calls with exactly one non-generic signature."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
shared = runpy.run_path(str(here.parent / "call-resolution-partition/analyze.py"))
prefix = shared["PREFIX"]
source = subprocess.check_output(
    ["git", "show", "e1eeaab:packages/tsc-go/internal/checker/checker.go"],
    cwd=here, text=True,
)
site, = (i for i, line in enumerate(source.splitlines(), 1)
         if "if !c.isSignatureApplicable(s.node, s.args, candidate, relation, CheckModeNormal," in line)
manifest = json.loads((here / "manifest.json").read_text())
report = {}
for name, project in manifest["projects"].items():
    path = here / f"{name}-cpu.pb.gz"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == project["profiles"]["cpu"]
    raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", path], text=True)
    phases = Counter()
    expressions = Counter()
    object_children = Counter()
    mutable_children = Counter()
    total = 0
    for cpu, frames in shared["decode"](raw):
        total += cpu
        names = [f[0].removeprefix(prefix) for f in frames]
        if "checkExpressionForMutableLocation" in names:
            mutable = names.index("checkExpressionForMutableLocation")
            child = names[mutable-1] if mutable else "(self)"
            mutable_children[child] += cpu
        boundary = next((i for i, n in enumerate(names) if n in shared["BOUNDARIES"]), len(frames))
        if "chooseOverload" not in names[:boundary]:
            continue
        choice = names.index("chooseOverload")
        if frames[choice][2] != site:
            continue
        if not choice or names[choice-1] != "isSignatureApplicable":
            phases["(call site without applicability frame)"] += cpu
            continue
        phase = names[choice-2] if choice >= 2 else "(self)"
        phases[phase] += cpu
        if phase == "checkExpressionWithContextualType":
            worker = next((i for i in reversed(range(choice-2)) if names[i] == "checkExpressionWorker"), None)
            kind = names[worker-1] if worker else "(outside expression dispatch)"
            expressions[kind] += cpu
            if kind == "checkObjectLiteral":
                child = names[worker-2] if worker >= 2 else "(self)"
                object_children[child] += cpu
    assert sum(object_children.values()) == expressions["checkObjectLiteral"]
    assert sum(expressions.values()) == phases["checkExpressionWithContextualType"]
    report[name] = dict(totalCpuNs=total, singleSignatureApplicabilityNs=sum(phases.values()),
                        phasesNs=dict(phases.most_common()), expressionHandlersNs=dict(expressions.most_common()),
                        objectLiteralChildrenNs=dict(object_children.most_common()),
                        allMutableLocationChildrenNs=dict(mutable_children.most_common()))
out = json.dumps(report, indent=2) + "\n"
if "--write" in sys.argv:
    (here / "single-signature.json").write_text(out)
else:
    assert out == (here / "single-signature.json").read_text()
