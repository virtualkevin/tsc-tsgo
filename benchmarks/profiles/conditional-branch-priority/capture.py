import hashlib
import json
from pathlib import Path
import sys
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects
ref=json.loads((here.parent/"conditional-union-work/counts.json").read_text())
binary=Path(sys.argv[1]).resolve()
report={"observerSha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"bits":["fixedInference","lowerQuality","equalQualityAfterReset","cachedNonMaxPriority"],"projects":{}}
for name,commit,matrix in observed_projects(binary):
    counts={f"{i},{j}":n for i,row in enumerate(matrix) for j,n in enumerate(row) if n}
    original=ref["projects"][name]
    assert original["commit"]==commit and sum(counts.values())==original["absentBefore"]+original["presentBefore"]
    report["projects"][name]={"commit":commit,"trueFalseMasks":counts}
    print(name,counts,flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
