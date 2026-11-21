"""Record which completed Sentry narrowing passes use only simple resolved cells."""
import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
reference = json.loads((here/"counts.json").read_text())["projects"]["sentry"]
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
          "cellRows":["otherType", "intersection", "apparentSelf", "cachedNonPartialProperty",
                      "resolvedOther", "ownResolvedSynthetic", "resolvedInstantiated", "resolvedMapped"],
          "cellColumns":["nil", "undefined", "unionContainingUndefined", "otherNonStructured",
                         "otherStructured", "differentFromPrior"],
          "passRows":["uncovered","allResolvedMappedAcceptUndefined"], "passColumns":["passes","queries"]}
for name, commit, rows in observed_projects(binary, projects={"sentry"}):
    assert commit == reference["commit"]
    expected = [sum(reference["groups"][k][i] for k in ("firstAbsent", "changedAbsentNames", "repeatAbsentNames")) for i in (0,1)]
    assert len(rows["cells"]) == 8 and all(len(row)==6 for row in rows["cells"])
    passes, queries = [sum(col) for col in zip(*rows["passes"], strict=True)]
    assert passes == expected[0] and 0 < queries <= expected[1]
    assert sum(map(sum,rows["cells"])) == queries
    report["priorInclusiveQueries"] = expected[1]
    report[name] = {"commit":commit, **rows}
(here/"cells.json").write_text(json.dumps(report,indent=2)+"\n")
print(report,flush=True)
