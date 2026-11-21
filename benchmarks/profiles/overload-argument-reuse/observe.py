"""Measure repeated contextual argument checks inside one overload resolution."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3] / "packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True, parents=True)
overlay = {}

def source(path):
    return subprocess.check_output(["git", "show", "e1eeaab:packages/tsc-go/" + path], cwd=root,text=True)

def save(path,text):
    target = out / Path(path).name
    target.write_text(text)
    overlay[str(root/path)] = str(target)

def change(s, before, after):
    assert s.count(before) == 1, before
    return s.replace(before, after)

path = "internal/checker/checker.go"
s = change(source(path),"type Checker struct {","type Checker struct {\n argumentProbe *argumentProbeFrame")
marker = "func (c *Checker) resolveCall(node *ast.Node, signatures []*Signature, candidatesOutArray *[]*Signature, checkMode CheckMode, callChainFlags SignatureFlags, headMessage *diagnostics.Message) *Signature {"
s = change(s,marker,marker + """
    previous := c.argumentProbe
    c.argumentProbe = &argumentProbeFrame{node:node}
    defer func(){ c.argumentProbe = previous }()
""")
for phase,ctx in enumerate(("context","nil /*inferenceContext*/")):
    expr = f"argType := c.checkExpressionWithContextualType(arg, paramType, {ctx}, checkMode)"
    s = change(s,expr, f"before := c.TotalInstantiationCount\n"+expr+f"\n c.observeArgument(node,signature,arg,paramType,argType,{ctx},checkMode,{phase},before)")
s += """
type argumentProbeKey struct { arg *ast.Node; param *Type }
type argumentProbeValue struct { result *Type; sig *Signature; context *InferenceContext; mode CheckMode }
type argumentProbeFrame struct { node *ast.Node; seen map[argumentProbeKey]argumentProbeValue }
var argumentCounts [2][7]atomic.Uint64

func (c *Checker) observeArgument(node *ast.Node, sig *Signature, arg *ast.Node, param, result *Type, context *InferenceContext, mode CheckMode, phase int, before uint32) {
    f := c.argumentProbe
    if f == nil || f.node != node { return }
    if f.seen == nil { f.seen = make(map[argumentProbeKey]argumentProbeValue) }
    row := &argumentCounts[phase]
    row[0].Add(1)
    key := argumentProbeKey{arg,param}
    if prev,ok := f.seen[key]; ok {
        row[1].Add(1)
        if prev.sig != sig { row[2].Add(1) }
        if prev.result != result { row[3].Add(1) }
        if prev.mode == mode && prev.context == context {
            row[4].Add(1)
            if prev.result != result { row[5].Add(1) }
            if before != c.TotalInstantiationCount { row[6].Add(1) }
        }
    }
    f.seen[key] = argumentProbeValue{result,sig,context,mode}
}
func ArgumentCounts() (r [2][7]uint64) {
    for i := range r { for j := range r[i] { r[i][j]=argumentCounts[i][j].Load() } }
    return r
}
"""
save(path,s)
path = "cmd/tsgo/main.go"
s = change(source(path), '"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
save(path,change(s,"os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.ArgumentCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
