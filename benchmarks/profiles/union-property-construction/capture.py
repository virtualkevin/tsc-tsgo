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
for name, commit, values in observed_projects(binary):
    assert len(values)==22 and sum(values[:2])>0 and all(isinstance(v,int) and v>=0 for v in values)
    groups={}
    for i,label in enumerate(("alreadyResolved","reference","mapped","other")):
        groups[label]=dict(zip(("calls","instantiations","createdTypes","createdSymbols","propertyCountAfter"),
                               values[2+5*i:7+5*i],strict=True))
    assert all(groups["alreadyResolved"][k]==0 for k in ("instantiations","createdTypes","createdSymbols"))
    report["projects"][name]={"commit":commit,"plainObject":values[0],"otherApparentInputs":values[1],"heuristic":groups}
    print(name,values,flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
