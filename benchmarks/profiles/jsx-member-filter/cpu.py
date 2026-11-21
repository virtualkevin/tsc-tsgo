"""Attribute the filter source line, separating member discovery from filtering."""
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
source = subprocess.check_output(["git","show","bd1baea:packages/tsc-go/internal/checker/jsx.go"],cwd=here,text=True)
site, = (i for i,line in enumerate(source.splitlines(),1)
         if "discriminantMembers := core.Filter(c.getPropertiesOfType(contextualType)" in line)
digest=hashlib.sha256(path.read_bytes()).hexdigest()
assert digest==json.loads((base/"profiles.json").read_text())["binaries"]["control"]["cpu"]
shared = runpy.run_path(str(here.parent/"call-resolution-partition/analyze.py"))
raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
total = 0
children = Counter()
predicate = Counter()
for ns, frames in shared["decode"](raw):
    total += ns
    names = [f[0].removeprefix(shared["PREFIX"]) for f in frames]
    candidates = [i for i,n in enumerate(names) if n=="discriminateContextualTypeByJSXAttributes" and frames[i][2]==site]
    if not candidates: continue
    i = candidates[0]
    children[names[i-1] if i else "(self)"] += ns
    fn = "discriminateContextualTypeByJSXAttributes.func2"
    if fn in names[:i]:
        j=names.index(fn)
        predicate[names[j-1] if j else "(self)"] += ns
report={"profileSha256":digest,"totalCpuNs":total,"filterSourceLine":site,"filterLineChildrenNs":children,
        "filterPredicateChildrenNs":predicate}
data=json.dumps(report,indent=2,sort_keys=True)+"\n"
if "--write" in sys.argv:
    (here/"cpu.json").write_text(data)
else: assert (here/"cpu.json").read_text()==data
