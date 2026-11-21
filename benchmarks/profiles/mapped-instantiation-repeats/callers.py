"""Rank callers of the outermost type-instantiation entry in size-aware Sentry."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys

here=Path(__file__).resolve().parent
profile=here.parent/"grouped-pointer-probes/advised-cpu.pb.gz"
binary=here.parents[2]/"packages/tsc-go/dist/tsc-go-large-heap-pages"
raw=subprocess.check_output([sys.argv[1],"-raw",binary,profile],text=True)
samples,locations=raw.split("Locations\n",1)
frames={}
for line in locations.split("Mappings\n")[0].splitlines():
    m=re.match(r"^\s*(\d+):\s+0x[\da-f]+(?:\s+M=\d+)?\s+(.*)",line)
    if m:
        addr=int(m[1]); frames[addr]=[]; line=m[2]
    m=re.match(r"(.+?)\s+(\S+):(\d+):\d+(?:\s+s=\d+(?:\(.*\))?)?$",line.strip())
    if m:
        frames[addr].append((m[1],m[2],int(m[3])))
prefix="github.com/microsoft/typescript-go/internal/"
entries={prefix+"checker.(*Checker)."+n for n in ("instantiateType","instantiateTypeWithAlias","instantiateTypeWorker")}
# Inline stacks are leaf-first. Attribute each sample to the first worker
# reached from the outer entry, including time in that worker's callees.
source=subprocess.check_output(
    ["git","show","395df1a:packages/tsc-go/internal/checker/checker.go"],
    cwd=here.parents[2],text=True,
).splitlines()
branch_at={}
in_worker=False
branch="worker entry"
for lineno,line in enumerate(source,1):
    if line.startswith("func "):
        in_worker="func (c *Checker) instantiateTypeWorker(" in line
    if in_worker:
        if line.startswith("\tcase "):
            branch=line.strip().removeprefix("case ").removesuffix(":")
        branch_at[lineno]=branch
by_branch=Counter()
conditional_lines=Counter()
evaluation_lines=Counter()
true_branch_kinds=Counter()
true_union_sites=Counter()
constituent_sites=Counter()
constituent_leaves=Counter()
nested_conditional_sites=Counter()
nested_direct_evaluation=Counter()
extends_worker_sites=Counter()
keyof_sites=Counter()
counts=Counter()
total=0
def first_callee(stack, end, name):
    """Find the first matching function entered below the exclusive end frame."""
    full_name=prefix+"checker.(*Checker)."+name
    return next((i for i in range(end-1,-1,-1) if stack[i][0]==full_name),None)

def site_at(stack, index, missing):
    if index is None:
        return missing
    line=stack[index][2]
    return f"{line} {source[line-1].strip()}"

def attribute_constituents(stack, union_index, ns):
    child=first_callee(stack,union_index,"instantiateTypeWorker")
    site=site_at(stack,child,"outside nested worker")
    constituent_sites[site]+=ns
    constituent_leaves[stack[0][0].removeprefix(prefix)]+=ns
    if child is None or branch_at[stack[child][2]]!="flags&TypeFlagsConditional != 0":
        return
    inst=first_callee(stack,child,"getConditionalTypeInstantiation")
    site=site_at(stack,inst,"outside nested conditional instantiation")
    nested_conditional_sites[site]+=ns
    if inst is not None and source[stack[inst][2]-1].strip()=="result = c.getConditionalType(root, newMapper, forConstraint, alias)":
        nested=first_callee(stack,inst,"getConditionalType")
        nested_direct_evaluation[site_at(stack,nested,"outside nested evaluation")]+=ns
        if nested is not None and source[stack[nested][2]-1].strip()=="extendsType := c.instantiateType(root.extendsType, mapper)":
            worker=first_callee(stack,nested,"instantiateTypeWorker")
            extends_worker_sites[site_at(stack,worker,"outside extends worker")]+=ns
            if worker is not None and source[stack[worker][2]-1].strip()=="return c.getIndexType(c.instantiateType(t.Target(), m))":
                index_call=first_callee(stack,worker,"getIndexTypeEx")
                keyof_sites[site_at(stack,index_call,"before or outside getIndexTypeEx")]+=ns

for line in samples.splitlines():
    m=re.match(r"^\s+\d+\s+(\d+):\s*(.*)$",line)
    if not m: continue
    ns=int(m[1]); total+=ns
    stack=[f for a in map(int,m[2].split()) for f in frames[a]]
    evaluation=first_callee(stack,len(stack),"getConditionalType")
    if evaluation is not None:
        n=stack[evaluation][2]
        evaluation_lines[f"{n} {source[n-1].strip()}"]+=ns
        if source[n-1].strip()=="result = c.instantiateType(trueType, trueMapper)":
            index=first_callee(stack,evaluation,"instantiateTypeWorker")
            if index is None:
                true_branch_kinds["outside worker"]+=ns
            else:
                line=stack[index][2]
                kind=branch_at[line]
                true_branch_kinds[kind]+=ns
                if kind=="flags&TypeFlagsUnionOrIntersection != 0":
                    statement=source[line-1].strip()
                    true_union_sites[f"{line} {statement}"]+=ns
                    if statement=="newTypes := c.instantiateTypes(types, m)":
                        attribute_constituents(stack,index,ns)
    outer=next((i for i in range(len(stack)-1,-1,-1) if stack[i][0] in entries),None)
    if outer is not None:
        if outer+1==len(stack):
            caller="truncated stack"
        else:
            name,path,lineno=stack[outer+1]
            caller=f"{name.removeprefix(prefix)} {path.removeprefix(prefix)}:{lineno}"
        counts[caller]+=ns
        if caller.startswith("checker.(*Checker).getTypeAliasInstantiation "):
            worker=next((f for f in reversed(stack[:outer+1])
                         if f[0]==prefix+"checker.(*Checker).instantiateTypeWorker"),None)
            branch=branch_at[worker[2]] if worker else "outside worker"
            by_branch[branch]+=ns
            if branch=="flags&TypeFlagsConditional != 0":
                frame=next((f for f in reversed(stack[:outer+1])
                            if f[0]==prefix+"checker.(*Checker).getConditionalTypeInstantiation"),None)
                site=f"{frame[2]} {source[frame[2]-1].strip()}" if frame else "outside conditional instantiation"
                conditional_lines[site]+=ns
assert total==json.loads((here/"cpu.json").read_text())["sentry-size-aware"]["totalCpuNs"]
report=dict(totalCpuNs=total,instantiationCpuNs=sum(counts.values()),callersNs=dict(counts.most_common()))
assert sum(by_branch.values())==sum(ns for caller,ns in counts.items()
                                    if caller.startswith("checker.(*Checker).getTypeAliasInstantiation "))
assert sum(conditional_lines.values())==by_branch["flags&TypeFlagsConditional != 0"]
expected=sum(ns for site,ns in true_union_sites.items() if site.endswith("newTypes := c.instantiateTypes(types, m)"))
assert sum(constituent_sites.values())==sum(constituent_leaves.values())==expected
report["nestedKeyofSitesNs"]=dict(keyof_sites.most_common())
report["nestedExtendsWorkerSitesNs"]=dict(extends_worker_sites.most_common())
report["nestedDirectEvaluationSitesNs"]=dict(nested_direct_evaluation.most_common())
report["nestedConstituentConditionalSitesNs"]=dict(nested_conditional_sites.most_common())
report["constituentWorkerSitesNs"]=dict(constituent_sites.most_common())
report["topConstituentLeafFunctionsNs"]=dict(constituent_leaves.most_common(10))
report["selectedTrueUnionOrIntersectionSiteNs"]=dict(true_union_sites.most_common())
report["selectedTrueBranchWorkerNs"]=dict(true_branch_kinds.most_common())
report["outerConditionalEvaluationSiteNs"]=dict(evaluation_lines.most_common())
report["aliasMissConditionalSiteNs"]=dict(conditional_lines.most_common())
report["aliasMissWorkerBranchNs"]=dict(by_branch.most_common())
(here/"callers.json").write_text(json.dumps(report,indent=2)+"\n")
print(round(100*sum(counts.values())/total,2),counts.most_common(6))
