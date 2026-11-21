import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
sys.dont_write_bytecode = True
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(), "projects":{}}
columns = ("wideningQueries", "repeatQueries", "differentType", "instantiated", "createdType",
           "createdSymbol", "changedInstantiationBudget", "changedRelationSizes", "nilOnRepeat")
quoted = "--quoted-jsx" in sys.argv
for name, commit, values in observed_projects(binary, projects={"sentry"} if quoted else None):
    assert 0 <= values[1] <= values[0] and all(0 <= v <= values[1] for v in values[2:])
    report["projects"][name] = {"commit":commit, **dict(zip(columns,values,strict=True))}
    print(name, values, flush=True)
(here/("quoted-jsx.json" if quoted else "counts.json")).write_text(json.dumps(report,indent=2)+"\n")
