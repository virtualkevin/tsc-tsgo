"""Separate first and second contextual lookups by stack in the matched Sentry control."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

here = Path(__file__).resolve().parent
base = here.parent/"object-instantiation-hits"
path = base/"sentry-control-cpu.pb.gz"
digest = hashlib.sha256(path.read_bytes()).hexdigest()
assert digest == json.loads((base/"profiles.json").read_text())["binaries"]["control"]["cpu"]
shared = runpy.run_path(str(here.parent/"call-resolution-partition/analyze.py"))
raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", path], text=True)
total = 0
jsx = Counter()
jsx_calls = {}
apparent_calls = {}
mutable = Counter()
for cpu, frames in shared["decode"](raw):
    total += cpu
    names = [f[0].removeprefix(shared["PREFIX"]) for f in frames]
    if "checkExpressionForMutableLocation" not in names:
        continue
    i = names.index("checkExpressionForMutableLocation")
    child = names[i-1] if i else "(self)"
    mutable[child] += cpu
    if "getContextualTypeForJsxAttribute" in names[:i]:
        jsx[child] += cpu
        j = names.index("getContextualTypeForJsxAttribute")
        leaf = names[j-1] if j else "(self)"
        jsx_calls.setdefault(child, Counter())[leaf] += cpu
        if leaf == "getApparentTypeOfContextualType":
            apparent_child = names[j-2] if j >= 2 else "(self)"
            apparent_calls.setdefault(child, Counter())[apparent_child] += cpu
report = {"profileSha256":digest, "totalCpuNs":total, "mutableByImmediateChildNs":mutable,
          "withJsxAttributeLookupBelowMutableNs":jsx, "jsxAttributeImmediateChildNs":jsx_calls,
          "jsxApparentTypeImmediateChildNs":apparent_calls}
result = json.dumps(report,indent=2,sort_keys=True)+"\n"
if "--write" in sys.argv:
    (here/"cpu.json").write_text(result)
else:
    assert (here/"cpu.json").read_text() == result
