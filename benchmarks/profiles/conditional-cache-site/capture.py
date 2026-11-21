import hashlib
import json
from pathlib import Path
import sys
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects
ref=json.loads((here.parent/"conditional-branch-priority/counts.json").read_text())
binary=Path(sys.argv[1]).resolve()
report={"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"bits":ref["bits"]+["cachedOriginalSourceAndBranch","immediateBranchGuard"],"projects":{}}
for name,commit,data in observed_projects(binary):
    counts={f"{i},{j}":v for i,row in enumerate(data["rows"]) for j,v in enumerate(row) if v}
    folded={}
    for key,v in counts.items():
        i,j=map(int,key.split(","))
        k=f"{i&15},{j&15}"
        folded[k]=folded.get(k,0)+v
    old=ref["projects"][name]
    assert old["commit"]==commit and folded==old["trueFalseMasks"]
    decls={k.split("/upstream/benchmarks/"+name+"/")[-1]:v for k,v in data["declarations"].items()}
    report["projects"][name]={"commit":commit,"trueFalseMasks":counts,"resolvedRowsByDeclaration":dict(sorted(decls.items(),key=lambda x:-x[1]))}
    print(name,counts,list(report["projects"][name]["resolvedRowsByDeclaration"].items())[:3],flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
