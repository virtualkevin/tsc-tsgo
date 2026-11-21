"""Check the observation build against a control on each frozen workload."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("control", type=Path)
p.add_argument("observer", type=Path)
p.add_argument("output", type=Path)
p.add_argument("--operand-details", action="store_true", help="read counters from the split operand/union observer")
args = p.parse_args()
root = Path(__file__).resolve().parents[3]
compilers = {"control": args.control.resolve(), "observer": args.observer.resolve()}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

fields = "calls distinct previouslyCompleted sameAsFirst activeAtEntry repeatInstantiated errorResult".split()
if args.operand_details:
    fields += ("operandInstantiated unionInstantiated identicalOperands existingPairCacheShape "
               "outsidePairCache twoOutsidePairCache changedResultOutside unionInstantiatedOutside").split()
report = {"binarySha256": {k: sha(v) for k, v in compilers.items()}, "projects": {}}
# Distinct keyof syntax nodes request the same named intersection. Also check a
# rejected key so the compiler must resolve the resulting key union.
fixture = """type Combined = { left: 1 } & { right: 2 };
declare let a: keyof Combined;
declare let b: keyof Combined;
a = "left";
b = "right";
a = "absent";
"""
with tempfile.TemporaryDirectory() as tmp:
    cwd = Path(tmp)
    (cwd / "input.ts").write_text(fixture)
    diagnostics = []
    env = {**os.environ, "TSC_TS_LIB_DIR": str(root / "upstream/typescript-go/internal/bundled/libs")}
    for role, binary in compilers.items():
        r = subprocess.run([binary,"--ignoreConfig","input.ts","--noEmit","--strict","--skipLibCheck","--pretty","false"],
                           cwd=cwd,env=env,capture_output=True,text=True,timeout=60)
        assert r.returncode == 1 and r.stdout.count("error TS2322:")==1, r
        diagnostics.append(r.stdout)
        if role=="observer":
            match=re.fullmatch(r"\[([\d ]+)\]\n",r.stderr)
            assert match,r.stderr
            counts=dict(zip(fields,map(int,match[1].split()),strict=True))
            assert counts["previouslyCompleted"]>=1 and counts["sameAsFirst"]>=1, counts
        else:
            assert not r.stderr
    assert diagnostics[0]==diagnostics[1]
    report["fixture"] = dict(source=fixture, diagnostics=diagnostics[0], counts=counts)
for group in ("small", "large"):
    ref = json.loads((root / f"benchmarks/results/native-project-inlining/{group}.json").read_text())
    env = {k: v for k,v in os.environ.items()
           if k not in ref["environment"]["unsetEnvironment"] and not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
    env.update(ref["environment"]["compilerEnvironment"])
    for project in ref["projects"]:
        cwd = Path(project["cwd"])
        assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==project["commit"]
        for item in project["preflight"]["candidate"]["inputs"]:
            assert sha(cwd / item["file"]) == item["sha256"]
        work = {}
        for role, binary in compilers.items():
            r = subprocess.run([binary,*project["compilerArgs"]["candidate"],"--extendedDiagnostics"],
                               cwd=cwd,env=env,capture_output=True,text=True,timeout=400,check=True)
            assert not re.search(r"error TS\d+",r.stdout)
            work[role] = dict((k,int(v)) for k,v in re.findall(r"^(Files|Lines|Identifiers|Types|Symbols|Instantiations):\s*(\d+)\s*$", r.stdout,re.M))
            assert len(work[role])==6
            if role=="control":
                assert not r.stderr
            else:
                match=re.fullmatch(r"\[([\d ]+)\]\n",r.stderr)
                assert match,r.stderr
                counts=dict(zip(fields,map(int,match[1].split()),strict=True))
                assert counts["sameAsFirst"] <= counts["previouslyCompleted"] <= counts["calls"]
                assert counts["distinct"] + counts["previouslyCompleted"] <= counts["calls"]
                assert counts["repeatInstantiated"] <= counts["previouslyCompleted"]
                if args.operand_details:
                    assert counts["identicalOperands"] == counts["existingPairCacheShape"] + counts["outsidePairCache"]
                    assert counts["identicalOperands"] <= counts["previouslyCompleted"]
                    assert counts["unionInstantiatedOutside"] <= counts["unionInstantiated"]
                    assert counts["twoOutsidePairCache"] <= counts["outsidePairCache"]
                    assert max(counts["operandInstantiated"], counts["unionInstantiated"]) <= counts["repeatInstantiated"]
        report["projects"][project["name"]] = dict(commit=project["commit"], counts=counts, work=work)
        print(project["name"],counts,"matched work",work["control"]==work["observer"],flush=True)
# TypeORM controls can vary in the symbol count. Keep uninstrumented repeats
# whenever the instrumented and control summaries disagree.
if report["projects"]["typeorm"]["work"]["control"] != report["projects"]["typeorm"]["work"]["observer"]:
    ref = json.loads((root / "benchmarks/results/native-project-inlining/small.json").read_text())
    project = next(p for p in ref["projects"] if p["name"]=="typeorm")
    env = {k: v for k,v in os.environ.items()
           if k not in ref["environment"]["unsetEnvironment"] and not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
    env.update(ref["environment"]["compilerEnvironment"])
    samples = []
    for _ in range(3):
        r = subprocess.run([compilers["control"],*project["compilerArgs"]["candidate"],"--extendedDiagnostics"],
                           cwd=project["cwd"],env=env,capture_output=True,text=True,timeout=400,check=True)
        assert not r.stderr
        sample = dict((k,int(v)) for k,v in re.findall(r"^(Files|Lines|Identifiers|Types|Symbols|Instantiations):\s*(\d+)\s*$",r.stdout,re.M))
        assert len(sample)==6
        samples.append(sample)
    report["typeormControlRepeats"] = samples
args.output.write_text(json.dumps(report,indent=2)+"\n")
