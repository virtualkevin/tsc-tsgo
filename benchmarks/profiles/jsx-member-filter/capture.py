"""Measure filter coverage on pinned Sentry and on wide JSX attribute lists."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

here = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path[:0] = [str(here.parent), str(here.parent/"jsx-absent-discriminants")]
from frozen_checks import observed_projects
import scaling

binary = Path(sys.argv[1]).resolve()
columns = ("eligibleFilters","hits","memberPredicateCallsSkipped","selectedMembersOnHits")
def row(values):
    assert len(values) == 4 and 0 <= values[1] <= values[0] and values[2] >= values[3] >= 0
    return dict(zip(columns, values))
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"fixture":{}}
scaling.bins = {"observer":binary}
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    for width in (1,16,256,1024):
        source = scaling.grouped_program(width,False).encode()
        (cwd/"case.tsx").write_bytes(source)
        run,_ = scaling.invoke("observer",["--noEmit"],cwd)
        assert run.returncode == 0 and not run.stdout
        result = row(json.loads(run.stderr))
        assert result["eligibleFilters"] >= width
        report["fixture"][width] = {"sourceSha256":scaling.sha(source), **result}
for name, commit, values in observed_projects(binary,projects={"sentry"}):
    report[name] = {"commit":commit, **row(values)}
    print(report[name],flush=True)
(here/"coverage.json").write_text(json.dumps(report,indent=2)+"\n")
