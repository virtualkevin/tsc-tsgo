"""Count signature-cache hits, miss causes and outcomes for frozen full checks."""
from pathlib import Path
import hashlib
import json
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = dict(observerSha256=hashlib.sha256(binary.read_bytes()).hexdigest(), projects={})
columns = ["requests","hits","firstResolution","activeReentry","candidateListRecheck","deferredMarkerRecheck","otherRepeat","usedInnerResult","restoredForFlow","returnedMarker"]
for name,commit,values in observed_projects(binary):
    rows = {}
    for scope,counts in zip(("other","callUnderInitializerArgumentInference"),values,strict=True):
        requests,hits,*rest = counts
        assert requests == hits + sum(rest[:5]) and all(v>=0 for v in counts)
        rows[scope] = dict(zip(columns,counts,strict=True))
    report["projects"][name] = dict(commit=commit,counts=rows)
    print(name,values,flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
