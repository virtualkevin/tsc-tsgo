"""Measure inclusive CPU and first checker callee on the most recent archived Sentry control."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
decoder = runpy.run_path(str(here.parent / "call-resolution-partition/analyze.py"))
profile = here.parent / "inherited-member-capacity/sentry-control-cpu.pb.gz"
digest = hashlib.sha256(profile.read_bytes()).hexdigest()
assert digest == json.loads(profile.with_name("profiles.json").read_text())["binaries"]["control"]["cpu"]
raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", profile], text=True)
operations = ("getLiteralTypeFromProperties", "resolvePendingObjectTypeMembers", "isSignatureApplicable",
              "inferTypeArguments", "checkApplicableSignatureForJsxCallLikeElement", "inferJsxTypeArguments",
              "createJsxAttributesTypeFromAttributesProperty", "checkJsxAttribute",
              "getApparentTypeOfContextualType", "discriminateContextualTypeByJSXAttributes",
              "getContextualTypeForJsxAttribute", "getEffectiveFirstArgumentForJsxSignature", "getTypeOfSymbol", "instantiateTypeWithAlias")
buckets = {op: Counter() for op in operations}
total = 0
for ns, frames in decoder["decode"](raw):
    total += ns
    names = [name.removeprefix(decoder["PREFIX"]) for name, _, _ in frames]
    for op in operations:
        if op in names:
            i = names.index(op)
            child = names[i-1] if i else "(self)"
            buckets[op][child] += ns
report = {"profileSha256": digest, "totalCpuNs": total, "operations": {}}
for op, children in buckets.items():
    cpu = sum(children.values())
    report["operations"][op] = {"inclusiveCpuNs": cpu, "percent": 100 * cpu / total,
                                "topChildrenCpuNs": dict(children.most_common(5))}
(here / "cpu.json").write_text(json.dumps(report, indent=2) + "\n")
