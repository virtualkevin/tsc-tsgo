"""Capture operation classes for work underneath cross-wrapper hits."""
import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
ref = json.loads((here/"counts.json").read_text())
mode = sys.argv[2] if len(sys.argv) == 3 else "classes"
assert mode in ("classes","--union-shape","--union-member")
report = {"binarySha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
          "columns": ["hits", "nestedInstantiations", "workDifferentFromPrevious",
                      "resultDifferentFromPrevious", "resultEqualsInput"], "projects":{}}
for name, commit, data in observed_projects(binary, projects={"sentry"} if mode != "classes" else None):
    assert ref["projects"][name]["commit"] == commit
    rows = dict(sorted(data.items(), key=lambda kv:-kv[1][1]))
    if mode == "--union-member":
        previous = json.loads((here/"union_shape.json").read_text())
        matching = [row for key,row in previous["projects"][name]["classes"].items()
                    if key.startswith("params=0 constants=1 other=1 origin=false alias=false active=false ")]
        assert [sum(row[i] for row in rows.values()) for i in range(5)] == [
            sum(row[i] for row in matching) for i in range(5)]
    elif mode == "--union-shape":
        previous = json.loads((here/"classes.json").read_text())
        observed = previous["projects"][name]["classes"]["union/*checker.ArrayTypeMapper"]
        assert [sum(row[i] for row in rows.values()) for i in range(5)] == observed
    else:
        previous = ref["projects"][name]["keys"]["inputAndMapper"]
        for column, field in [(0,"crossWrapperHits"), (1,"nestedInstantiationsOnHit"), (3,"differentResultOnHit")]:
            assert sum(row[column] for row in rows.values()) == previous[field]
    report["projects"][name] = {"commit":commit, "classes":rows}
    print(name, list(rows.items())[:3], flush=True)
filename = {"classes":"classes.json","--union-shape":"union_shape.json","--union-member":"union_member.json"}[mode]
(here/filename).write_text(json.dumps(report, indent=2)+"\n")
