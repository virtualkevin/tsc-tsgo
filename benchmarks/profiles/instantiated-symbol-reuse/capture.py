import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
keys = ["targetAndMapper", "inputAndMapper", "inputAndSimpleMapping"]
fields = ["requests", "nestedInstantiations", "crossWrapperHits", "nestedInstantiationsOnHit",
          "differentResultOnHit", "hitsWithInstantiations", "tableClears"]
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
          "capacityPerCheckerPerKey": 32768, "projects": {}}
for project, commit, rows in observed_projects(binary):
    data = {key:dict(zip(fields, row, strict=True)) for key,row in zip(keys, rows, strict=True)}
    assert data[keys[0]]["requests"] == data[keys[1]]["requests"] >= data[keys[2]]["requests"]
    assert all(r["requests"] >= r["crossWrapperHits"] >= r["differentResultOnHit"] for r in data.values())
    report["projects"][project] = {"commit": commit, "keys": data}
    print(project, rows, flush=True)
(here/"counts.json").write_text(json.dumps(report, indent=2)+"\n")
