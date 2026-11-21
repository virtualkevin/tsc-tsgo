"""Observe actual span hits on Sentry and on a four-way mapped union."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path
sys.dont_write_bytecode = True
import scaling
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from frozen_checks import observed_projects

binary = Path(sys.argv[1]).resolve()
columns = ["changedWatchedValue","preferredEntryReplacement","plansBuilt","spanAttempts","skippedSpans","skippedNames","skippedLookups"]
report = {"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"columns":columns,"widths":{}}
def check(row):
    assert len(row)==len(columns) and all(isinstance(v,int) and v>=0 for v in row)
    assert row[3] >= row[4] and row[5] >= row[4]
    return dict(zip(columns,row,strict=True))
other = "--other-projects" in sys.argv[2:]
if not other:
    with tempfile.TemporaryDirectory() as tmp:
        cwd = Path(tmp)
        scaling.bins={"observer":binary}
        for n in (1,16,256,1024):
            src=scaling.grouped_program(n,False).encode()
            (cwd/"case.tsx").write_bytes(src)
            r,_=scaling.invoke("observer",["--noEmit"],cwd)
            assert r.returncode==0 and not r.stdout
            report["widths"][n]={"inputSha256":scaling.sha(src),**check(json.loads(r.stderr))}
for name,commit,row in observed_projects(binary, projects=({"vscode","typeorm","trpc"} if other else {"sentry"})):
    report[name]={"commit":commit,**check(row)}
print(report)
(here/("group-counts-other.json" if other else "group-counts.json")).write_text(json.dumps(report,indent=2)+"\n")
