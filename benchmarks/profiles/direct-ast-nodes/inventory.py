"""Count reachable direct-allocation syntax kinds per parsed file in the ordinary compiler."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]
module=root/"packages/tsc-go"
scratch=Path(sys.argv[1]).resolve()
scratch.mkdir(exist_ok=True)
generated=(module/"internal/ast/ast_generated.go").read_text()
# Associate concrete direct allocations with their returned syntax kinds.
kinds={}
for body in re.findall(r'func \(f \*NodeFactory\) New\w+\([^\n]*\n(.*?)\n}',generated,re.S):
    typ=re.search(r'data := &(\w+)\{\}',body)
    node=re.search(r'return f\.newNode\((Kind\w+), data\)',body)
    if typ and node:
        assert kinds.setdefault(node[1],typ[1])==typ[1]
types=sorted(set(kinds.values()))
assert "ObjectLiteralExpression" in types and "ImportClause" in types
path=module/"internal/compiler/fileloader.go"
s=path.read_text()
s=s.replace("import (",'import (\n "encoding/json"\n "os"',1)
site="\n\treturn sourceFile\n}"
assert s.count(site)==1
cases="\n".join(f"case ast.{k}: counts[{types.index(v)}]++" for k,v in sorted(kinds.items()))
s=s.replace(site,"""
    if sourceFile != nil {
        var counts [N]int
        var visit ast.Visitor
        visit = func(n *ast.Node) bool {
            switch n.Kind { CASES }
            n.ForEachChild(visit)
            return false
        }
        sourceFile.ForEachChild(visit)
        row, err := json.Marshal([]any{t.normalizedFilePath,counts})
        if err != nil {panic(err)}
        os.Stderr.Write(append(row,'\\n'))
    }
    return sourceFile
}""".replace("[N]",f"[{len(types)}]").replace("CASES",cases))
edited=scratch/"fileloader.go"
edited.write_text(s)
overlay=scratch/"inventory-overlay.json"
overlay.write_text(json.dumps({"Replace":{str(path):str(edited)}}))
binary=scratch/"inventory"
subprocess.run([os.environ.get("GO","go"),"build","-buildvcs=false",f"-overlay={overlay}","-o",binary,"./cmd/tsgo"],cwd=module,check=True)
ref=json.loads(gzip.decompress((here.parent/"template-union-compaction/native.json.gz").read_bytes()))
env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","TS_GO_","SCRIPTC_"))}
env.update(ref["environment"]["compilerEnvironment"])
report={"types":types,"kinds":kinds,"binarySha256":hashlib.sha256(binary.read_bytes()).hexdigest(),"projects":{}}
for p in ref["projects"]:
    cwd=Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
    inputs={str((cwd/f["file"]).resolve()):f for f in p["preflight"]["candidate"]["inputs"]}
    for name,f in inputs.items(): assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==f["sha256"]
    proc=subprocess.run([binary,*p["fileDiscoveryArgs"]["candidate"]],cwd=cwd,env=env,capture_output=True,text=True,check=True,timeout=300)
    assert sorted(str((cwd/f).resolve()) for f in proc.stdout.splitlines())==sorted(inputs)
    rows=[]
    for line in proc.stderr.splitlines():
        name,counts=json.loads(line)
        resolved=str((cwd/name).resolve())
        if resolved in inputs:
            assert len(counts)==len(types) and min(counts)>=0
            rows.append([inputs[resolved]["file"],{t:n for t,n in zip(types,counts,strict=True) if n}])
    rows.sort()
    assert [r[0] for r in rows]==sorted(i["file"] for i in inputs.values())
    raw=json.dumps(rows,separators=(",",":")).encode()
    (here/(p["name"]+".json.gz")).write_bytes(gzip.compress(raw,mtime=0))
    report["projects"][p["name"]]={"commit":p["commit"],"files":len(rows),"sha256":hashlib.sha256(raw).hexdigest()}
    print(p["name"],len(rows),flush=True)
(here/"inventory.json").write_text(json.dumps(report,indent=2)+"\n")
