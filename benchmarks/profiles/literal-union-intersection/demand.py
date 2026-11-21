"""Measure checker-path demand on each frozen project and verify a positive control."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
ref = json.loads(gzip.decompress((here.parent / "template-union-compaction/native.json.gz").read_bytes()))
binary = Path(sys.argv[1]).resolve()
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])

def counts(cwd, args):
    r = subprocess.run([binary, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=400, check=True)
    assert not r.stdout, r.stdout
    all_calls, eligible, members = json.loads(r.stderr)
    assert all_calls >= eligible >= 0 and members >= eligible * 64
    return dict(primitiveIntersections=all_calls, eligiblePairs=eligible, eligibleMembers=members)

report = {"probeSha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "projects": {}}
with tempfile.TemporaryDirectory() as tmp:
    a = " | ".join(f'"k{i:06}"' for i in range(0,256,2))
    b = " | ".join(f'"k{i:06}"' for i in range(0,256,3))
    (Path(tmp) / "stress.ts").write_text(f'type A = {a};\ntype B = {b};\nconst overlap: A & B = "k000006";')
    report["positiveControl"] = counts(tmp, ["--ignoreConfig","--strict","--noEmit","--lib","es5","stress.ts"])
    assert report["positiveControl"]["eligiblePairs"] > 0
for project in ref["projects"]:
    cwd = Path(project["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"], cwd=cwd, text=True).strip() == project["commit"]
    for item in project["preflight"]["candidate"]["inputs"]:
        assert hashlib.sha256((cwd / item["file"]).read_bytes()).hexdigest() == item["sha256"]
    value = counts(cwd, project["compilerArgs"]["candidate"])
    report["projects"][project["name"]] = dict(commit=project["commit"], **value)
    print(project["name"], value, flush=True)
(here / "demand.json").write_text(json.dumps(report, indent=2) + "\n")
