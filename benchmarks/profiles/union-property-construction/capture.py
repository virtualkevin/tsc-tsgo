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
    assert len(values)==47 and sum(values[:2])>0 and all(isinstance(v,int) and v>=0 for v in values)
    groups={}
    for i,label in enumerate(("alreadyResolved","reference","mapped","other")):
        groups[label]=dict(zip(("calls","instantiations","createdTypes","createdSymbols","propertyCountAfter",
                                "callsWithInstantiations","callsCreating64PlusSymbols","symbolsIn64PlusCalls"),
                               values[2+8*i:10+8*i],strict=True))
    assert all(groups["alreadyResolved"][k]==0 for k in ("instantiations","createdTypes","createdSymbols"))
    registered,dropped,inside,after=values[34:38]
    assert inside+after<=registered
    demand={"recorded":registered,"dropped":dropped,"firstAccessorInsideResolution":inside,
            "firstAccessorOutsideResolution":after,"neverReachedAccessor":registered-inside-after}
    cohorts={}
    for i,label in enumerate(("other","explicitStringKeyWithoutRemapping","keyofStringKeyWithoutRemapping")):
        n,a,b=values[38+3*i:41+3*i]
        assert a+b<=n
        cohorts[label]={"recorded":n,"firstAccessorInside":a,"firstAccessorOutside":b}
    assert sum(x["recorded"] for x in cohorts.values())==registered
    assert sum(x["firstAccessorInside"] for x in cohorts.values())==inside
    assert sum(x["firstAccessorOutside"] for x in cohorts.values())==after
    demand["cohorts"]=cohorts
    report["projects"][name]={"commit":commit,"plainObject":values[0],"otherApparentInputs":values[1],"heuristic":groups,"newMappedMemberDemand":demand}
    print(name,values,flush=True)
(here/"counts.json").write_text(json.dumps(report,indent=2)+"\n")
