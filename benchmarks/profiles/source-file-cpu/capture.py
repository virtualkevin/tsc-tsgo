"""Find hot source files and count samples in generic inference and property relations."""
from collections import Counter,defaultdict
from pathlib import Path
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

here=Path(__file__).resolve().parent
ref=json.loads(gzip.decompress((here.parent/"literal-union-intersection/native.json.gz").read_bytes()))
binary,go=(Path(x).resolve() for x in sys.argv[1:])
env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
report=dict(binarySha256=sha(binary),projects={})
for p in sorted(ref["projects"],key=lambda p:len(p["preflight"]["candidate"]["inputs"])):
    cwd=Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
    inputs={(cwd/i["file"]).resolve():i["sha256"] for i in p["preflight"]["candidate"]["inputs"]}
    assert all(sha(f)==h for f,h in inputs.items())
    with tempfile.TemporaryDirectory() as tmp:
        r=subprocess.run([binary,*p["compilerArgs"]["candidate"],"--pprofDir",tmp],cwd=cwd,env=env,capture_output=True,text=True,check=True,timeout=480)
        assert not r.stderr and all(l.startswith(("CPU profile: ","Memory profile: ")) for l in r.stdout.splitlines())
        profile,=Path(tmp).glob("*-cpuprofile.pb.gz")
        dest=here/f"{p['name']}.pb.gz"
        dest.write_bytes(profile.read_bytes())
    raw=subprocess.check_output([go,'tool','pprof','-raw',dest],text=True)
    stacks,locations=raw.split("Locations\n",1)
    frames=defaultdict(str)
    loc=None
    for line in locations.split("Mappings\n")[0].splitlines():
        m=re.match(r'^\s*(\d+):\s+0x[0-9a-f]+',line)
        if m: loc=int(m[1])
        if loc is not None:frames[loc]+=line+'\n'
    rows=defaultdict(Counter)
    total=0
    for line in stacks.splitlines():
        m=re.fullmatch(r'\s*\d+\s+(\d+):\s*([\d ]*)',line)
        if m:
            weight=int(m[1])
            total+=weight
            ids=[int(i) for i in m[2].split()]
        elif 'ts-file:[' in line:
            label=re.fullmatch(r'\s*ts-file:\[(.*)\]',line)
            assert label,line
            path=(cwd/label[1]).resolve()
            assert path in inputs,path
            row=rows[os.path.relpath(path,cwd)]
            row['cpuNs']+=weight
            if any('.inferTypeArguments ' in frames[i] for i in ids):row['inferenceNs']+=weight
            if any('.propertiesRelatedTo ' in frames[i] for i in ids):row['propertiesNs']+=weight
    tagged=sum(row['cpuNs'] for row in rows.values())
    assert total>=tagged>0
    top=sorted(rows.items(),key=lambda kv:kv[1]['cpuNs'],reverse=True)
    report['projects'][p['name']]=dict(commit=p['commit'],profileSha256=sha(dest),totalCpuNs=total,labelledCpuNs=tagged,sampledFiles=len(rows),files=dict(top))
    print(p['name'],total,tagged,top[:3],flush=True)
(here/'results.json').write_text(json.dumps(report,indent=2)+'\n')
