"""Observe callee type computations on both paths of a declaration initializer."""
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
s = change(source(path), "type Checker struct {", "type Checker struct {\n observedCall *initializerObservation")
s = change(s, "initializer := declaration.Initializer()\n\tt := c.getQuickTypeOfExpression(initializer)", """initializer := declaration.Initializer()
    previous := c.observedCall
    frame := initializerObservation{node: ast.SkipParentheses(initializer)}
    c.observedCall = &frame
    defer func(){ c.observedCall = previous }()
    t := c.getQuickTypeOfExpression(initializer)
    if frame.callee != nil {
        initCallCounts[0].Add(1)
        if t == nil {
            frame.fallback = true
            initCallCounts[1].Add(1)
        }
    }""")
s = change(s,"return c.getReturnTypeOfSingleNonGenericSignature(c.checkNonNullExpression(expr.Expression()), SignatureKindCall)", """raw := c.checkExpression(expr.Expression())
        if frame := c.observedCall; frame != nil && frame.node == expr && !frame.fallback {
            frame.callee = raw
        }
        return c.getReturnTypeOfSingleNonGenericSignature(c.checkNonNullType(raw,expr.Expression()), SignatureKindCall)""")
s = change(s, "funcType := c.checkExpression(node.Expression())\n\tif isCallChain(node)", """before := c.TotalInstantiationCount
    funcType := c.checkExpression(node.Expression())
    if f := c.observedCall; f != nil && f.fallback && f.node == node {
        initCallCounts[2].Add(1)
        if !f.seen { f.seen = true; initCallCounts[3].Add(1) }
        if f.callee != funcType { initCallCounts[4].Add(1) }
        if c.TotalInstantiationCount != before { initCallCounts[5].Add(1) }
    }
    if isCallChain(node)""")
s += """
type initializerObservation struct { node *ast.Node; callee *Type; fallback, seen bool }
var initCallCounts [6]atomic.Uint64
func InitializerCallCounts() (result [6]uint64) {
    for i := range result { result[i] = initCallCounts[i].Load() }
    return result
}
"""
save(path,s)
path = "cmd/tsgo/main.go"
s = change(source(path), '"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
save(path,change(s,"os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.InitializerCallCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
