"""Find separately allocated syntax kinds in historical full-check heap samples."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import tarfile

here=Path(__file__).resolve().parent
prior=here.parent/"ast-arena-audit"
parser=runpy.run_path(str(prior/"analyze.py"))["parse"]
source=subprocess.check_output(["git","show","50291d2:packages/tsc-go/internal/ast/ast_generated.go"],cwd=here,text=True)
methods=dict(re.findall(r'^func \(f \*NodeFactory\) (New\w+)\([^\n]+\n\s*data := &(\w+)\{\}',source,re.M))
prefix="github.com/microsoft/typescript-go/internal/ast.(*NodeFactory)."
report={"scope":"Historical full-check sampled heap data. Only samples with a generated factory constructor at the leaf and a direct concrete allocation in that constructor are included. Includes parsing and other factory users. Weighted object/byte estimates, not exact counts or timing.","factorySourceSha256":hashlib.sha256(source.encode()).hexdigest(),"projects":{}}
with tarfile.open(prior/"raw-heaps.tar.gz") as archive:
    for inp in json.loads((prior/"inputs.json").read_text()):
        project=inp["project"]
        raw=archive.extractfile(project+".raw.txt").read()
        assert hashlib.sha256(raw).hexdigest()==inp["rawSha256"]
        byType=Counter()
        objects=Counter()
        allocs=storage=0
        for (n,b,_,_),frames in parser(raw.decode()):
            allocs+=n
            storage+=b
            leaf=frames[0]
            if leaf.startswith(prefix) and (t:=methods.get(leaf[len(prefix):])):
                byType[t]+=b
                objects[t]+=n
        report["projects"][project]=dict(rawSha256=inp["rawSha256"],totalObjects=allocs,totalBytes=storage,
            sampledDirectObjects=objects.total(),sampledDirectBytes=byType.total(),
            topByObjects=[dict(kind=t,objects=n,bytes=byType[t]) for t,n in objects.most_common(10)])
        print(project,round(100*objects.total()/allocs,2),round(100*byType.total()/storage,2),objects.most_common(3))
(here/"direct-nodes.json").write_text(json.dumps(report,indent=2)+"\n")
