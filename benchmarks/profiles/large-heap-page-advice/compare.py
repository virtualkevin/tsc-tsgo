"""Compare three full compilers in balanced three-run blocks on pinned projects."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from statistics import median
import subprocess
import tempfile
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("control", type=Path)
parser.add_argument("advised", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
assert not args.output.exists()
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

bins = {"native":root/"packages/tsc-ts/dist/tsc-original","control":args.control.resolve(),"advised":args.advised.resolve()}
report = {"binaries":{k:digest(v) for k,v in bins.items()}, "projects":{}}
assert report["binaries"]["advised"] == json.loads((here/"pages.json").read_text())["binarySha256"]
assert report["binaries"]["control"] == json.loads((here.parent/"heap-page-confirmation/builds.json").read_text())["builds"]["control"]["sha256"]
def save():
    args.output.write_text(json.dumps(report,indent=2)+"\n")
with tempfile.TemporaryDirectory() as temp:
    metrics = Path(temp)/"resources"
    for group in ("small","large"):
        reference = json.loads((root/f"benchmarks/results/native-project-inlining/{group}.json").read_text())
        assert report["binaries"]["native"] == reference["binaries"]["baseline"]["sha256"]
        env = {k:v for k,v in os.environ.items() if k not in reference["environment"]["unsetEnvironment"]
               and not k.startswith(("TSC_", "TS_GO_", "SCRIPTC_"))}
        env.update(reference["environment"]["compilerEnvironment"], LC_ALL="C")
        for index, project in enumerate(reference["projects"]):
            name = project["name"]
            cwd = Path(project["cwd"])
            inputs = project["preflight"]["baseline"]["inputs"]
            def verify():
                assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip() == project["commit"]
                assert not subprocess.check_output(["git","status","--porcelain","--untracked-files=no"],cwd=cwd)
                for item in inputs:
                    assert digest(cwd/item["file"]) == item["sha256"]
                assert {k:digest(v) for k,v in bins.items()} == report["binaries"]
            verify()
            command = project["compilerArgs"]["baseline"]
            assert command == project["compilerArgs"]["candidate"]
            for binary in bins.values():
                result = subprocess.run([binary,*command,"--listFilesOnly"],cwd=cwd,env=env,capture_output=True,text=True,check=True,timeout=400)
                assert not result.stderr
                assert sorted(os.path.relpath(cwd / line,cwd) for line in result.stdout.splitlines()) == sorted(i["file"] for i in inputs)
            rows = []
            # Reverse the cycle on the second project so both relative orders occur on the large inputs.
            base = list(bins) if not index else list(reversed(bins))
            orders = [base[i:]+base[:i] for i in range(3)]
            if group == "small":
                orders += [list(reversed(order)) for order in orders]
            for block, order in enumerate([base]+orders):
                for mode in order:
                    start = time.monotonic_ns()
                    proc = subprocess.run(["/usr/bin/time","-f","%U %S %M %R %F","-o",metrics,bins[mode],*command],
                                          cwd=cwd,env=env,capture_output=True,check=True,timeout=400)
                    elapsed = (time.monotonic_ns()-start)/1e6
                    assert not proc.stdout and not proc.stderr
                    user,system,rss,minor,major = metrics.read_text().split()
                    rows.append(dict(block=block,mode=mode,ms=elapsed,userSeconds=float(user),systemSeconds=float(system),
                                     rssKiB=int(rss),minorFaults=int(minor),majorFaults=int(major)))
                print(name,block,{r["mode"]:round(r["ms"]) for r in rows[-3:]},flush=True)
            verify()
            stats = {k:{f:median(r[f] for r in rows if r["mode"]==k and r["block"]>0)
                        for f in ("ms","rssKiB","userSeconds","systemSeconds","minorFaults","majorFaults")} for k in bins}
            report["projects"][name] = dict(commit=project["commit"],configSha256=project["configSha256"],
                                            args=command,files=len(inputs),rows=rows,medians=stats)
            save()
report["status"]="passed"
save()
