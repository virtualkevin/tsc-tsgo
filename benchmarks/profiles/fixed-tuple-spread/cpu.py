"""Measure inclusive CPU budgets, counting each stack once per operation."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
decoder = runpy.run_path(str(here.parent / "call-resolution-partition/analyze.py"))
groups = {
    "normalizeTuple": {"(*TupleNormalizer).normalize"},
    "conditional": {"(*Checker).getConditionalType"},
    "permissive": {"(*Checker).getPermissiveInstantiation"},
    "inference": {"(*Checker).getInferredType"},
    "signatureApplicability": {"(*Checker).isSignatureApplicable"},
    "jsxAttributes": {"(*Checker).createJsxAttributesTypeFromAttributesProperty"},
}
report = {}
for build, folder, manifest_name, suffix in [
    ("ordinary", "public-native-cpu", "go.json", "-go.pb.gz"),
    ("shipping", "shipped-cpu-costs", "manifest.json", "-cpu.pb.gz"),
]:
    base = here.parent / folder
    manifest = json.loads((base / manifest_name).read_text())
    report[build] = {}
    for name, entry in manifest["projects"].items():
        profile = base / (name + suffix)
        digest = hashlib.sha256(profile.read_bytes()).hexdigest()
        assert digest == (entry["cpuProfileSha256"] if build == "ordinary" else entry["profiles"]["cpu"])
        raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", profile], text=True)
        totals = dict.fromkeys(groups, 0)
        paths = Counter()
        direct_children = Counter()
        props_children = Counter()
        total = 0
        for ns, frames in decoder["decode"](raw):
            total += ns
            checker = {f[0].split("/checker.", 1)[1] for f in frames if "/checker." in f[0]}
            names = [f[0].removeprefix(decoder["PREFIX"]) for f in frames]
            if "getEffectiveFirstArgumentForJsxSignature" in names:
                pos = names.index("getEffectiveFirstArgumentForJsxSignature")
                chain = list(reversed(names[:pos]))
                sub = chain[:2]
                if len(sub) == 2 and sub[1] == "getJsxManagedAttributesFromLocatedAttributes":
                    sub = chain[:4]
                props_children[" / ".join(sub) or "(self)"] += ns
            if "isSignatureApplicable" in names:
                owner = names.index("isSignatureApplicable")
                chain = list(reversed(names[:owner]))
                dispatch = {"checkExpressionWithContextualType", "checkExpressionEx", "checkExpressionWorker"}
                index = next((i for i, n in enumerate(chain) if n not in dispatch), len(chain))
                handler = chain[index] if index < len(chain) else "(self)"
                child = chain[index + 1] if index + 1 < len(chain) else "(self)"
                paths[handler] += ns
                direct_children[(handler, child)] += ns
            for group, functions in groups.items():
                if checker & functions:
                    totals[group] += ns
        assert paths.total() == direct_children.total() == totals["signatureApplicability"]
        print(build, name, total, totals, flush=True)
        report[build][name] = dict(profileSha256=digest, totalNs=total, inclusiveNs=totals, jsxPropsPathNs=dict(props_children.most_common()), applicabilityPathNs=dict(paths.most_common()), applicabilityChildNs={f'{h} / {c}': ns for (h,c),ns in direct_children.most_common()})
(here / "cpu.json").write_text(json.dumps(report, indent=2) + "\n")
