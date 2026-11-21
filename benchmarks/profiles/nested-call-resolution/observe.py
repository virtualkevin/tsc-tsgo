"""Partition signature resolution misses during initializer argument inference."""
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
s = change(source(path),"type Checker struct {","type Checker struct {\n signatureHistory map[*ast.Node]uint32; initDepth, argDepth int")
site="func (c *Checker) checkDeclarationInitializer(declaration *ast.Node, checkMode CheckMode, contextualType *Type) *Type {"
s=change(s,site,site+"\n c.initDepth++; defer func(){c.initDepth--}()")
site="argType := c.checkExpressionWithContextualType(arg, paramType, context, checkMode)"
s=change(s,site,"if c.initDepth != 0 { c.argDepth++ }; "+site+"; if c.initDepth != 0 { c.argDepth-- }")
start=s.index("func (c *Checker) getResolvedSignature(")
end=s.index("\nfunc ",start+1)
body=s[start:end]
body=change(body,"cached := links.resolvedSignature","""cached := links.resolvedSignature
    group := 0
    if c.argDepth != 0 && ast.IsCallExpression(node) { group = 1 }
    row := &signatureProbe[group]
    row[0].Add(1)""")
body=change(body,"return cached","row[1].Add(1); return cached")
body=change(body,"saveResolutionStart := c.resolutionStart", """if c.signatureHistory == nil { c.signatureHistory = make(map[*ast.Node]uint32) }
    active, seen := c.signatureHistory[node]
    switch {
    case !seen: row[2].Add(1)
    case active != 0: row[3].Add(1)
    case candidatesOutArray != nil: row[4].Add(1)
    case cached == c.resolvingSignature: row[5].Add(1)
    default: row[6].Add(1)
    }
    c.signatureHistory[node] = active + 1
    saveResolutionStart := c.resolutionStart""")
body=change(body,"result = links.resolvedSignature","row[7].Add(1); result = links.resolvedSignature")
body=change(body,"links.resolvedSignature = cached","row[8].Add(1); links.resolvedSignature = cached")
body=change(body,"return result","if result == c.resolvingSignature { row[9].Add(1) }; c.signatureHistory[node] = active; return result")
s=s[:start]+body+s[end:]+"""
var signatureProbe [2][10]atomic.Uint64
func SignatureCounts() (r [2][10]uint64) {
    for i := range r { for j := range r[i] { r[i][j]=signatureProbe[i][j].Load() } }
    return r
}
"""
save(path,s)
path = "cmd/tsgo/main.go"
s = change(source(path), '"context"', '"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"')
save(path,change(s,"os.Exit(runMain())","status := runMain(); json.NewEncoder(os.Stderr).Encode(checker.SignatureCounts()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
