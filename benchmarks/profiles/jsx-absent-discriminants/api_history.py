"""Compare identical sequences of contextual queries, signature help and diagnostics."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

here = Path(__file__).resolve().parent
root = here.parents[2] / "packages/tsc-go"
go = sys.argv[1]
with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp)
    subprocess.run([sys.executable, here/"watched.py", work],check=True)
    overlays = {"control":{}, "candidate":json.loads((work/"overlay.json").read_text())["Replace"]}
    histories = {}
    for name, files in overlays.items():
        files[str(root/"internal/checker/absent_api_history_test.go")] = str(here/"api_test.go.txt")
        overlay = work/(name+"-api.json")
        overlay.write_text(json.dumps({"Replace":files}))
        output = work/(name+"-calls.json")
        subprocess.run([go,"test","-overlay",overlay,"./internal/checker","-run","^TestAbsentGroupsServiceHistory$","-count=1"],
                       cwd=root,env={**os.environ,"TSC_GO_API_RECORD":str(output)},check=True)
        histories[name] = json.loads(output.read_text())
    assert histories["control"] == histories["candidate"]
    (here/"api-history.json").write_text(json.dumps(histories,indent=2)+"\n")
