"""Compare observer work counts with the size-aware Go compiler on pinned inputs."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]
control = root/"packages/tsc-go/dist/tsc-go-large-heap-pages"
observer = Path(sys.argv[1]).resolve()
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
report = {"controlSha256":digest(control), "observerSha256":digest(observer), "projects":{}}
assert report["controlSha256"] == json.loads((here.parent/"large-heap-page-advice/pages.json").read_text())["binarySha256"]
fields = ("requests","misses","calls","distinctInputs","previouslyCompleted","sameResultAsFirst","alreadyActive","errorResults")
for group in ("small","large"):
    reference=json.loads((root/f"benchmarks/results/native-project-inlining/{group}.json").read_text())
    env = {k:v for k,v in os.environ.items() if k not in reference["environment"]["unsetEnvironment"]
           and not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
    env.update(reference["environment"]["compilerEnvironment"])
    for p in reference["projects"]:
        cwd = Path(p["cwd"])
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
        for item in p["preflight"]["candidate"]["inputs"]:
            assert digest(cwd/item["file"])==item["sha256"]
        stats={}
        for mode, binary in (("control",control),("observer",observer)):
            r=subprocess.run([binary,*p["args"],"--extendedDiagnostics"],cwd=cwd,env=env|{"TSC_MAPPED_REPORT":"1"},
                             capture_output=True,text=True,timeout=400,check=True)
            assert not re.search(r"error TS\d+",r.stdout)
            stats[mode]={k:int(v) for k,v in re.findall(r"^(Files|Lines|Identifiers|Types|Symbols|Instantiations):\s*(\d+)\s*$",r.stdout,re.M)}
            assert len(stats[mode])==6
            if mode=="control":
                assert not r.stderr
            else:
                m=re.fullmatch(r"\[([\d ]+)\]\n",r.stderr)
                assert m,r.stderr
                counts=dict(zip(fields,map(int,m[1].split()),strict=True))
                assert counts["sameResultAsFirst"]<=counts["previouslyCompleted"]<=counts["calls"]<=counts["misses"]<=counts["requests"]
                assert counts["distinctInputs"]+counts["previouslyCompleted"]<=counts["calls"]
        report["projects"][p["name"]]=dict(commit=p["commit"],counts=counts,work=stats)
        print(p["name"],counts,"work matches",stats["control"]==stats["observer"],flush=True)
(here/"results.json").write_text(json.dumps(report,indent=2)+"\n")
