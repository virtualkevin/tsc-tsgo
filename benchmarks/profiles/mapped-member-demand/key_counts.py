import hashlib
import json
from pathlib import Path
import sys

here=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(here.parent))
from frozen_checks import observed_projects

binary=Path(sys.argv[1]).resolve()
report={"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"projects":{}}
for name, commit, v in observed_projects(binary):
    assert len(v)==6 and v[0]>=v[1]>=v[2] and v[3]<=v[1]
    row=dict(zip(("newMappedSymbols","identicalKey","avoidedSecondaryEntryAtCreation","duplicatesPromoted",
                  "typeResolutionUsingName","typeResolutionUsingSeparateKey"),v,strict=True))
    report["projects"][name]={"commit":commit,**row}
    print(name,v,flush=True)
(here/"key-counts.json").write_text(json.dumps(report,indent=2)+"\n")
