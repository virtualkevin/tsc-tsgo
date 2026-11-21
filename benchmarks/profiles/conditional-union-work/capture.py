from pathlib import Path
import sys
import json
import hashlib

here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects

binary=Path(sys.argv[1]).resolve()
keys=["absentBefore","presentBefore","presentAfter","maxPriority","circularity","otherPriority","conditionalTargetRows","firstResolvedBranchPair","repeatResolvedBranchPair","bothPrimitiveOrConcreteSingleton"]
report={"observerSha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"maskBits":["priorityReset","equalPriority","addedContraCandidate","insertedCandidate","clearedTopLevel","reorderedCandidate"],"projects":{}}
for name,commit,data in observed_projects(binary):
    values,masks=data["values"],data["masks"]
    assert len(masks)==64 and sum(masks)==sum(values[:2])
    assert sum(values[:2])==sum(values[3:6]) and values[2]<=sum(values[:2])
    assert values[9]<=sum(values[7:9])<=values[6]
    report["projects"][name]={"commit":commit, "pairOutcomeMasks":{i:v for i,v in enumerate(masks) if v}, **dict(zip(keys,values,strict=True))}
    print(name, values, flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
