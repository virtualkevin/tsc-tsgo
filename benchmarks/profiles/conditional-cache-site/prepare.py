"""Locate the cached child and its conditional declaration on the real inputs."""
from pathlib import Path
import subprocess
import json
import sys

here=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve()
subprocess.run([sys.executable,here.parent/"conditional-branch-priority/prepare.py",out],check=True)
path=out/"inference.go"
s=path.read_text()
def change(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
change('"sync/atomic"', '"sync/atomic"\n"sync"\n"strconv"')
change('source,target *Type','source,target,branchType *Type')
assert s.count("n.observe.branch=i+1")==2
s=s.replace("n.observe.branch=i+1","n.observe.branch=i+1; n.observe.branchType=t")
change('n.observe.mask[i-1]|=8','''n.observe.mask[i-1]|=8
        if source==n.observe.source && target==n.observe.branchType {n.observe.mask[i-1]|=16}''')
site='if !c.couldContainTypeVariables(target) || c.isNoInferType(target) {'
change(site,site+'\n if i:=n.observe.branch; i>0 && source==n.observe.source && target==n.observe.branchType {n.observe.mask[i-1]|=32}')
change('var branchMasks [16][16]atomic.Uint64','''var branchMasks [64][64]atomic.Uint64
var declMu sync.Mutex
var declCounts=map[string]uint64{}''')
site='n.inferencePriority = min(n.inferencePriority, saveInferencePriority)\n\t\t\t\t}'
change(site,site+"""
                if len(sources)>=32 && t.flags&TypeFlagsConditional!=0 {
                    ct:=t.AsConditionalType()
                    node:=ct.root.node
                    if a,b:=ct.resolvedTrueType,ct.resolvedFalseType;a!=nil && b!=nil {
                        loc:=ast.GetSourceFileOfNode(node).FileName()+"@"+strconv.Itoa(node.Pos())+" true="+strconv.FormatUint(uint64(a.flags),16)+" false="+strconv.FormatUint(uint64(b.flags),16)
                        declMu.Lock(); declCounts[loc]++;declMu.Unlock()
                    }
                }""")
change('func BranchCounts() (rows [16][16]uint64) {','func BranchCounts() map[string]any {\n var rows [64][64]uint64')
change('return rows\n}', 'return map[string]any{"rows":rows,"declarations":declCounts}\n}')
path.write_text(s)
