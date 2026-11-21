"""Count repeat callee checks without replacing either computation."""
from pathlib import Path
import hashlib
import json
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = dict(observerSha256=hashlib.sha256(binary.read_bytes()).hexdigest(), projects={})
columns = ["quickCallee", "quickFellBack", "repeatCalleeChecks", "fallbacksWithRepeat", "differentTypeOnRepeat", "instantiatedOnRepeat"]
for name,commit,values in observed_projects(binary):
    quick,fallback,repeats,seen,different,instantiated = values
    assert quick >= fallback >= seen >= 0 and repeats >= max(different,instantiated,seen)
    report["projects"][name] = dict(commit=commit,counts=dict(zip(columns,values,strict=True)))
    print(name, report["projects"][name]["counts"],flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
