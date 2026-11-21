"""Measure directly attributed object-literal allocations on the frozen VS Code check."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from collections import Counter

here=Path(__file__).resolve().parent
go,control,candidate=sys.argv[1:4]
readback="--readback" in sys.argv[4:]
public=json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
p=next(x for x in public["projects"] if x["name"]=="vscode")
cwd=Path(p["cwd"])
inputs=p["preflight"]["candidate"]["inputs"]
env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","SCRIPTC_","TS_GO_","GODEBUG","GOMAXPROCS","GOGC","GOMEMLIMIT"))}
env.update(public["environment"]["compilerEnvironment"])
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify():
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
    assert all(sha(cwd/i["file"])==i["sha256"] for i in inputs)
report=dict(commit=p["commit"],files=len(inputs),args=p["compilerArgs"]["candidate"],samples={})
for engine,binary in (("control",control),("candidate",candidate)):
    verify()
    profile=here/(engine+"-vscode-mem.pb.gz")
    if readback:
        old=json.loads((here/"heap.json").read_text())["samples"][engine]
        assert sha(profile)==old["profileSha256"] and sha(binary)==old["binarySha256"]
    else:
        with tempfile.TemporaryDirectory() as tmp:
            run=subprocess.run([binary,*report["args"],"--pprofDir",tmp],cwd=cwd,env=env,capture_output=True,text=True,timeout=480,check=True)
            assert not run.stderr and len(run.stdout.splitlines())==2 and all(l.startswith(("Memory profile: ","CPU profile: ")) for l in run.stdout.splitlines())
            source,=Path(tmp).glob("*-memprofile.pb.gz")
            profile.write_bytes(source.read_bytes())
    raw=subprocess.check_output([go,"tool","pprof","-raw",profile],text=True)
    samples,locations=raw.split("Locations\n",1)
    assert "alloc_objects/count alloc_space/bytes" in samples
    frames={}
    for line in locations.split("Mappings\n")[0].splitlines():
        loc=re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)",line)
        if loc:
            slot=frames[loc[1]]=[]
            line=loc[2]
        frame=re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?",line)
        if frame:
            slot.append((frame[1],frame[3]))
    sites={"control":{"13221":"overwriteIndex","13282":"orderedMembers"},
           "candidate":{"13227":"overwriteIndex","13290":"orderedMembers"}}[engine]
    owned=Counter()
    lines=Counter()
    total=0
    for weight,stack in re.findall(r"^\s*\d+\s+(\d+)\s+\d+\s+\d+:\s*([\d ]+)$",samples,re.M):
        total+=int(weight)
        locations_in_sample=stack.split()
        leaf_frames=frames[locations_in_sample[0]]
        leaf=leaf_frames[0] if leaf_frames else None
        owner=next((line for loc in locations_in_sample for name,line in frames[loc] if name.endswith(".(*Checker).checkObjectLiteral")),None)
        if owner in sites: owned[sites[owner]]+=int(weight)
        if leaf and leaf[0].endswith(".(*Checker).checkObjectLiteral"):
            lines[leaf[1]]+=int(weight)
    assert lines
    report["samples"][engine]=dict(binarySha256=sha(binary),profileSha256=sha(profile),totalBytes=total,directBytes=lines.total(),temporaryCollectionBytes=dict(owned),directBytesByLine=dict(lines.most_common()))
    verify()
    print(engine,total,lines.total(),flush=True)
(here/"heap.json").write_text(json.dumps(report,indent=2)+"\n")
