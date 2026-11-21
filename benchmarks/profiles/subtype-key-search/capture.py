"""Collect checker-local subtype-key search counts on the four verified worktrees."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

here = Path(__file__).resolve().parent
root = here.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("observer", type=Path)
parser.add_argument("--merge-runs", action="store_true")
parser.add_argument("--output", type=Path, default=here/"results.json")
options = parser.parse_args()
observer = options.observer.resolve()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

control = json.loads((here.parent / "intersection-keyof-operands/results.json").read_text())
assert sha(root / "packages/tsc-go/dist/tsc-go") == control["binarySha256"]["control"]
fields = "searches propertiesTested repeatedSource repeatedProperties sameKeyAndType repeatsInstantiated repeatedNoKey foundKey emptySearch searchesInstantiated targetPairsExcluded".split()
if options.merge_runs:
    fields = "calls existingElements incomingElements append insert identical overlap overlapElements incomingAtLeast1024".split()
result = {"controlSourceRevision": "a261586", "controlSha256": control["binarySha256"]["control"],
          "observerSha256": sha(observer), "projects": {}}
for group in ("small", "large"):
    reference = json.loads((root / f"benchmarks/results/native-project-inlining/{group}.json").read_text())
    env = {k:v for k,v in os.environ.items()
           if k not in reference["environment"]["unsetEnvironment"] and not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
    env.update(reference["environment"]["compilerEnvironment"])
    for project in reference["projects"]:
        name = project["name"]
        cwd = Path(project["cwd"])
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==project["commit"]
        for item in project["preflight"]["candidate"]["inputs"]:
            assert sha(cwd / item["file"]) == item["sha256"]
        r = subprocess.run([observer,*project["compilerArgs"]["candidate"],"--extendedDiagnostics"],
                           cwd=cwd,env=env,capture_output=True,text=True,timeout=400,check=True)
        assert not re.search(r"error TS\d+",r.stdout)
        work = {k:int(v) for k,v in re.findall(r"^(Files|Lines|Identifiers|Types|Symbols|Instantiations):\s*(\d+)\s*$",r.stdout,re.M)}
        match = re.fullmatch(r"\[([\d ]+)\]\n",r.stderr)
        assert match and len(work)==6,r.stderr
        counts = dict(zip(fields,map(int,match[1].split()),strict=True))
        if options.merge_runs:
            assert sum(counts[k] for k in ("append","insert","identical","overlap")) == counts["calls"]
            assert counts["calls"] * 32 <= min(counts["existingElements"],counts["incomingElements"])
            assert counts["overlapElements"] <= counts["existingElements"]
        else:
            assert counts["searches"] >= counts["repeatedSource"] >= counts["sameKeyAndType"] >= counts["repeatedNoKey"]
            assert counts["propertiesTested"] >= counts["repeatedProperties"]
            assert counts["repeatsInstantiated"] <= counts["searchesInstantiated"]
            assert counts["foundKey"] <= counts["searches"]
        ref = control["projects"][name]
        assert ref["commit"] == project["commit"]
        result["projects"][name] = dict(commit=project["commit"],counts=counts,work=work,control=ref["work"]["control"])
        print(name, counts, flush=True)
options.output.write_text(json.dumps(result,indent=2)+"\n")
