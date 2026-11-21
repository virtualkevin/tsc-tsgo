"""Observe reachability-triggered overload resolution on full public-library inputs."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
overlay={str(root/"internal/checker/reach_probe.go"):str(here/"probe.go.txt")}
arguments = "--arguments" in sys.argv[3:]
if arguments:
    overlay[str(root/"internal/checker/arguments_probe.go")] = str(here/"arguments.go.txt")
def edit(name,changes):
    src=root/name
    s=src.read_text()
    if arguments and name=="internal/checker/checker.go":
        changes += [("type Checker struct {","type Checker struct {\n reachArgumentProbe reachArgumentProbe")]
        for params,phase in [("nil /*inferenceContext*/","apply"),("context","infer")]:
            original = "argType := c.checkExpressionWithContextualType(arg, paramType, "+params+", checkMode)"
            changes.append((original,'argType := c.observeReachArgument(node,arg,i,paramType,'+params+',checkMode,"'+phase+'")'))
    for old,new in changes:
        assert s.count(old)==1,old
        s=s.replace(old,new)
    if arguments:
        s=s.replace("signature=c.observeReachResolution(node,links.resolvedSignature)","signature=c.scopedReachResolution(node,links.resolvedSignature)")
        s=s.replace("checker.ReachCallCounts()","checker.ReachArgumentCounts()")
    dst=out/src.name
    dst.write_text(s)
    overlay[str(src)]=str(dst)
edit("internal/checker/checker.go",[
    ("type Checker struct {","type Checker struct {\n reachObserver reachObserver"),
    ("cached := links.resolvedSignature\n\tif cached", "cached := links.resolvedSignature\n c.observeLaterResolution(node,cached)\n if cached"),
])
edit("internal/checker/flow.go",[
    ("func (c *Checker) getEffectsSignature(node *ast.Node) *Signature {","func (c *Checker) getEffectsSignature(node *ast.Node) *Signature { return c.effectsSignatureObserved(node,false) }\nfunc (c *Checker) effectsSignatureObserved(node *ast.Node, reach bool) *Signature {\n measured:=false"),
    ("signature = c.getResolvedSignature(node, nil, CheckModeNormal)\n\t\t}", "if reach {measured=true; signature=c.observeReachResolution(node,links.resolvedSignature)} else { signature = c.getResolvedSignature(node,nil,CheckModeNormal) }\n}"),
    ("links.effectsSignature = signature","if measured {c.observeReachEffect(node,signature)}\n links.effectsSignature = signature"),
    ("if signature := c.getEffectsSignature(flow.Node); signature != nil {\n\t\t\t\tif predicate", "if signature := c.effectsSignatureObserved(flow.Node,true); signature != nil {\n\t\t\t\tif predicate"),
])
edit("cmd/tsgo/main.go",[
    ('"context"','"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ('os.Exit(runMain())','status:=runMain();json.NewEncoder(os.Stderr).Encode(checker.ReachCallCounts());os.Exit(status)'),
])
cfg=out/"overlay.json"
cfg.write_text(json.dumps({"Replace":overlay}))
binary=out/"tsgo"
subprocess.run([sys.argv[2],"build","-buildvcs=false","-overlay="+str(cfg),"-o",binary,"./cmd/tsgo"],cwd=root,check=True)
ref=json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
env={k:v for k,v in os.environ.items() if not k.startswith(("TSC_","SCRIPTC_","TS_GO_","GODEBUG","GOMAXPROCS","GOGC","GOMEMLIMIT"))}
env.update(ref["environment"]["compilerEnvironment"])
report=dict(binarySha256=hashlib.sha256(binary.read_bytes()).hexdigest(),projects={})
for p in ref["projects"]:
    cwd=Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
    inputs=p["preflight"]["candidate"]["inputs"]
    assert all(hashlib.sha256((cwd/f["file"]).read_bytes()).hexdigest()==f["sha256"] for f in inputs)
    result=subprocess.run([binary,*p["compilerArgs"]["candidate"]],cwd=cwd,env=env,text=True,capture_output=True,timeout=480,check=True)
    assert not result.stdout
    rows=json.loads(result.stderr) or []
    totals={}
    for row in rows:
        for name,v in row.items():
            if not arguments:
                assert v["Calls"]==v["Cached"]+v["Resolving"]+v["Cold"]==sum(v[k] for k in ("SelectedPredicate","SelectedAssertion","SelectedNever","Unknown","Other"))
                assert v["LaterSame"]<=v["LaterDemand"]<=v["ColdResultCached"]<=v["Cold"]
            acc=totals.setdefault(name,{})
            for k,n in v.items(): acc[k]=acc.get(k,0)+n
    report["projects"][p["name"]]=dict(commit=p["commit"],files=len(inputs),totals=totals,workers=rows)
    (here/("arguments.json.gz" if arguments else "counts.json.gz")).write_bytes(gzip.compress(json.dumps(report,sort_keys=True).encode(),mtime=0))
    if arguments:
        print(p["name"],sorted(((v["ElapsedNs"]/1e9,k) for k,v in totals.items()),reverse=True)[:6],flush=True)
        continue
    print(p["name"],sorted(((v["ExclusiveNs"]/1e9,k,v["Cold"],v["LaterSame"]) for k,v in totals.items()),reverse=True)[:5],flush=True)
