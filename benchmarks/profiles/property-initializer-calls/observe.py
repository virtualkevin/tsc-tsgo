"""Measure exclusive uncached resolution work per syntax node and checker."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
module = here.parents[2]/"packages/tsc-go"
scratch = Path(sys.argv[1]).resolve()
scratch.mkdir(parents=True,exist_ok=True)
phases = "--phases" in sys.argv[3:]
conditional = phases or "--conditionals" in sys.argv[3:]
probe = "conditional_probe.go.txt" if conditional else "probe.go.txt"
overlay = {str(module/"internal/checker/resolution_work_probe.go"):str(here/probe)}
if phases:
    source = (here/probe).read_text()
    source = source.replace("Types, Instantiations, Iterations uint64", "Types, Instantiations, Iterations uint64; ByStage [8]uint64")
    source = source.replace("w.Types += v.Types", "for i:=range w.ByStage { w.ByStage[i]+=v.ByStage[i] }; w.Types += v.Types")
    source = source.replace("type activeResolution struct {", "type activeResolution struct {\n stage int")
    dest = scratch/"stage_probe.go"
    dest.write_text(source)
    overlay[str(module/"internal/checker/resolution_work_probe.go")] = str(dest)
def edit(name, changes):
    path = module/name
    source = path.read_text()
    if conditional and name=="internal/checker/checker.go":
        changes += [
            ("c.TotalInstantiationCount++","c.TotalInstantiationCount++\n if a:=c.workerResolutionProbe.active;a!=nil {a.current.Instantiations++}"),
            ("c.TypeCount++","c.TypeCount++\n if a:=c.workerResolutionProbe.active;a!=nil {a.current.Types++}"),
            ("tailCount := 0","active:=c.workerResolutionProbe.active\n if active!=nil {prev:=active.current;defer func(){active.current=prev}()}\n tailCount := 0"),
            ("if tailCount == 1000 {","if active!=nil {active.enter(root)}\n if tailCount == 1000 {"),
        ]
    if phases and name=="internal/checker/checker.go":
        changes += [
            ("a.current.Instantiations++","a.current.Instantiations++;a.current.ByStage[a.stage]++"),
            ("prev:=active.current;defer func(){active.current=prev}()", "prev,stage:=active.current,active.stage;defer func(){active.current,active.stage=prev,stage}()"),
            ("active.enter(root)","active.enter(root);active.stage=0"),
        ]
        # Stage zero covers operand instantiation and the initial deferral checks.
        for stage,anchor in enumerate((
            "if len(root.inferTypeParameters) != 0 && !c.hasInferenceIndependentTagMismatch",
            "var inferredExtendsType *Type",
            "if inferredExtendsType.flags&TypeFlagsAnyOrUnknown == 0 && (checkType.flags",
            "if checkType.flags&TypeFlagsAny != 0 || forConstraint && inferredExtendsType.flags",
            "if inferredExtendsType.flags&TypeFlagsAnyOrUnknown != 0 || c.isTypeAssignableTo",
            "trueType := c.getTypeFromTypeNode(root.node.TrueType)",
            "result = c.newConditionalType(root, mapper, combinedMapper)",
        ),1):
            changes.append((anchor,"if active!=nil {active.stage="+str(stage)+"}\n"+anchor))
    for old,new in changes:
        assert source.count(old)==1, old
        source = source.replace(old,new)
    dest = scratch/path.name
    dest.write_text(source)
    overlay[str(path)] = str(dest)
edit("internal/checker/checker.go",[
    ("type Checker struct {","type Checker struct {\n workerResolutionProbe workerResolutionProbe"),
    ("result := c.resolveSignature(node, candidatesOutArray, checkMode)","result := c.observedResolution(node,candidatesOutArray,checkMode)"),
])
edit("cmd/tsgo/main.go",[
    ('"context"','"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())","status:=runMain();json.NewEncoder(os.Stderr).Encode(checker.ResolutionWorkReport());os.Exit(status)"),
])
cfg = scratch/"overlay.json"
cfg.write_text(json.dumps({"Replace":overlay}))
binary = scratch/"tsgo"
subprocess.run([sys.argv[2],"build","-buildvcs=false","-overlay="+str(cfg),"-o",binary,"./cmd/tsgo"],cwd=module,check=True)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
ref = json.loads(gzip.decompress((here.parent/"named-key-union/public.json.gz").read_bytes()))
env = {k:v for k,v in os.environ.items() if not k.startswith(("TSC_","SCRIPTC_","TS_GO_","GODEBUG","GOMAXPROCS","GOGC","GOMEMLIMIT"))}
env.update(ref["environment"]["compilerEnvironment"])
result = dict(binarySha256=sha(binary),checkerSha256=sha(module/"internal/checker/checker.go"),projects={})
if phases:
    prior = json.loads(gzip.decompress((here/"conditional.json.gz").read_bytes()))["projects"]
for p in ref["projects"]:
    cwd = Path(p["cwd"])
    assert subprocess.check_output(["git","rev-parse","HEAD"],cwd=cwd,text=True).strip()==p["commit"]
    inputs = p["preflight"]["candidate"]["inputs"]
    assert all(sha(cwd/i["file"])==i["sha256"] for i in inputs)
    run = subprocess.run([binary,*p["compilerArgs"]["candidate"]],cwd=cwd,env=env,text=True,capture_output=True,timeout=480,check=True)
    assert not run.stdout
    counts = json.loads(run.stderr)
    if phases:
        previous = prior[p["name"]]["counts"]
        assert counts.keys() == previous.keys()
        for decl, roots in counts.items():
            assert roots.keys() == previous[decl].keys()
            for root, cost in roots.items():
                assert sum(cost["ByStage"]) == cost["Instantiations"]
                assert all(cost[key] == value for key, value in previous[decl][root].items())
    result["projects"][p["name"]] = dict(commit=p["commit"],files=len(inputs),counts=counts)
    if conditional:
        print(p["name"],len(counts),"selected declarations",flush=True)
    else:
        print(p["name"],[(k,g["Nodes"],g["Work"]["Instantiations"]) for k,g in counts["Groups"].items()],flush=True)
    (here/("stages.json.gz" if phases else "conditional.json.gz" if conditional else "work.json.gz")).write_bytes(gzip.compress(json.dumps(result,sort_keys=True).encode(),mtime=0))
