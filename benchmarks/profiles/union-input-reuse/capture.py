"""Verify the frozen full checks and record reuse without skipping any union work."""
from pathlib import Path
import hashlib
import json
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = dict(observerSha256=hashlib.sha256(binary.read_bytes()).hexdigest(), slotsPerChecker=4096,
              groups=["otherShort","pureLiteralOrIntrinsic"], columns=["calls","simulatedHits","changedResultOnHit","instantiatedOnHit"], projects={})
for name,commit,result in observed_projects(binary):
    assert len(result["Rows"]) == 3 and result["Other"]>=0
    for group in result["Rows"]:
        for calls,hits,changed,instantiated in group:
            assert calls>=hits>=changed>=0 and hits>=instantiated>=0
    report["projects"][name] = dict(commit=commit,counts=result)
    print(name,result,flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
