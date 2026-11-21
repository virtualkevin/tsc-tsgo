"""Replay the same JSX editor queries on upstream, ordinary Go, and the bounded candidate."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
repo = here.parents[2]
fork = repo / "packages/tsc-go"
upstream = repo / "upstream/typescript-go"
revision = json.loads((fork/"UPSTREAM.json").read_text())["commit"]
assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=upstream,text=True).strip()==revision
assert not subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=upstream)
fixture = here.parent/"jsx-absent-discriminants/api_test.go.txt"
with tempfile.TemporaryDirectory() as temp:
    work = Path(temp)
    subprocess.run([sys.executable, here/"prepare.py", work, "--bounded"],check=True)
    candidate = json.loads((work/"overlay.json").read_text())["Replace"]
    histories = {}
    for name,root,files in [("upstream",upstream,{}),("control",fork,{}),("candidate",fork,candidate)]:
        files[str(root/"internal/checker/absent_api_history_test.go")] = str(fixture)
        overlay = work/(name+".json")
        overlay.write_text(json.dumps({"Replace":files}))
        output = work/(name+"-calls.json")
        subprocess.run([sys.argv[1],"test","-overlay",overlay,"./internal/checker","-run","^TestAbsentGroupsServiceHistory$","-count=1"],
                       cwd=root,env={**os.environ,"TSC_GO_API_RECORD":str(output)},check=True)
        histories[name] = json.loads(output.read_text())
    assert histories["upstream"] == histories["control"] == histories["candidate"]
    (here/"history.json").write_text(json.dumps({"upstream": revision, "queries":histories["candidate"]},indent=2)+"\n")
