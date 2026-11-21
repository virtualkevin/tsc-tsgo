"""Count repeated argument and parameter identities within each call resolution."""
from pathlib import Path
import hashlib
import json
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = dict(observerSha256=hashlib.sha256(binary.read_bytes()).hexdigest(), projects={})
columns = ["checks","repeatArgumentAndParameter","differentSignature","changedType","repeatWithSameModeAndContext","changedTypeSameModeAndContext","instantiatedSameModeAndContext"]
for name,commit,values in observed_projects(binary):
    rows = {}
    for phase,counts in zip(("inference","applicability"),values,strict=True):
        calls,repeats,different,changed,exact,unstable,instantiated = counts
        assert calls >= repeats >= max(different,changed,exact) and exact >= max(unstable,instantiated)
        rows[phase] = dict(zip(columns,counts,strict=True))
    report["projects"][name] = dict(commit=commit,counts=rows)
    print(name,values,flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
