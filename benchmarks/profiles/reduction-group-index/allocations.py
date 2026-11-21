"""Attribute sampled cumulative allocation bytes to JSX attribute construction call stacks."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from collections import Counter

here = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("go")
parser.add_argument("control")
parser.add_argument("candidate")
parser.add_argument("--sparse", action="store_true")
parser.add_argument("--readback", action="store_true")
options = parser.parse_args()
go = options.go
public = json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
sentry = next(p for p in public["projects"] if p["name"] == "sentry")
cwd = Path(sentry["cwd"])
inputs = sentry["preflight"]["candidate"]["inputs"]
args = sentry["compilerArgs"]["candidate"]
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_","SCRIPTC_","TS_GO_","GODEBUG","GOMAXPROCS","GOMEMLIMIT","GOGC"))}
env.update(public["environment"]["compilerEnvironment"])
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify():
    assert subprocess.check_output(["git","rev-parse","HEAD"], cwd=cwd,text=True).strip()==sentry["commit"]
    assert all(digest(cwd/i["file"]) == i["sha256"] for i in inputs)

def costs(profile):
    raw = subprocess.check_output([go,"tool","pprof","-raw",profile],text=True)
    samples,locations = raw.split("Locations\n",1)
    assert "alloc_objects/count alloc_space/bytes" in samples
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        m = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)",line)
        if m:
            slot = frames[int(m[1])] = []
            line = m[2]
        f = re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?",line)
        if f:
            slot.append((f[1],int(f[3])))
    total = Counter()
    by_child = Counter()
    by_line = Counter()
    grouping_lines = Counter()
    grouping_objects = Counter()
    for objects,space,stack in re.findall(r"^\s*(\d+)\s+(\d+)\s+\d+\s+\d+:\s*([\d ]+)$",samples,re.M):
        amount = int(space)
        ids = stack.split()
        entries = [f for i in ids for f in frames[int(i)]]
        total["all"] += amount
        jsx = next((i for i,(name,_) in enumerate(entries) if name.endswith(".createJsxAttributesTypeFromAttributesProperty")),None)
        reduction = any(name.endswith(".hasNeverReducedProperty") for name,_ in entries)
        if reduction: total["reductionInclusive"] += amount
        if jsx is None: continue
        total["jsx"] += amount
        if reduction: total["jsxWithReduction"] += amount
        child = entries[jsx-1][0].split(".")[-1] if jsx else "<local>"
        by_child[child] += amount
        by_line[entries[jsx][1]] += amount
        first = frames[int(ids[0])]
        if first and first[0][0].endswith(".hasNeverReducedProperty"):
            total["jsxWithReductionFlat"] += amount
            grouping_lines[first[0][1]] += amount
            grouping_objects[first[0][1]] += int(objects)
    assert sum(by_child.values()) == total["jsx"]
    return dict(bytes=total,jsxLinesBytes=dict(by_line.most_common()),jsxChildrenBytes=dict(by_child.most_common()),jsxFlatReductionLines=dict(grouping_lines.most_common()),
                jsxFlatReductionAllocObjects=dict(grouping_objects.most_common()))

manifest = here/("sparse-allocations.json" if options.sparse else "allocations.json")
report = {"args": args, "commit": sentry["commit"], "files": len(inputs), "samples": {}}
for engine, binary in [("control", options.control), ("candidate", options.candidate)]:
    label = ("sparse-" if options.sparse else "") + engine
    profile = here/(label+"-mem.pb.gz")
    if options.readback:
        prior = json.loads(manifest.read_text())["samples"][engine]
        assert prior["binarySha256"] == digest(binary) and prior["profileSha256"] == digest(profile)
    else:
        verify()
        with tempfile.TemporaryDirectory() as temp:
            run = subprocess.run([binary,*args,"--pprofDir",temp],cwd=cwd,env=env,capture_output=True,text=True,check=True,timeout=480)
            assert not run.stderr and len(run.stdout.splitlines())==2 and all(l.startswith(("Memory profile: ","CPU profile: ")) for l in run.stdout.splitlines())
            src, = Path(temp).glob("*-memprofile.pb.gz")
            profile.write_bytes(src.read_bytes())
        verify()
    report["samples"][engine] = dict(binarySha256=digest(binary),profileSha256=digest(profile),**costs(profile))
    print(label,report["samples"][engine]["bytes"],flush=True)
manifest.write_text(json.dumps(report,indent=2)+"\n")
