"""Record target visits, pair tests and matches by source width."""
import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),
          "widths":["0-1","2-7","8-31","32+"],
          "multipleColumns":["nonNakedTargets","calls","returnedAtFirstGuard"],
          "matchingPasses":["typeOrBaseIdentity","closeMatch","identity"],
          "shapes":["object","conditional","parameter","indexedAccess","template","intersection","union","literal","otherPrimitive","other"],
          "avoidedColumns":["passes","predicateCalls"],
          "matchingColumns":["invocations","predicateCalls","matches"],"projects":{}}
for project, commit, data in observed_projects(binary):
    for key, length in (("multiple",1),("matching",3)):
        assert len(data[key]) == length
        for widths in data[key]:
            assert len(widths) == 4
            assert all(0 <= hit <= count for _,count,hit in widths)
    assert sum(map(sum,data["wideSourceTargetShapes"])) == data["multiple"][0][3][1]
    assert data["avoided"][1] <= data["matching"][1][3][1]
    report["projects"][project] = {"commit":commit, **data}
    print(project, data, flush=True)
(here/"counts.json").write_text(json.dumps(report, indent=2)+"\n")
