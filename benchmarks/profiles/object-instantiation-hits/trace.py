"""Trace instantiation workers and nested cache outcomes inside optional handler substitution."""
from pathlib import Path
import json
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True,parents=True)
replacements = {}
def read(p):
    return subprocess.check_output(["git","show","0a28a53:packages/tsc-go/"+p],cwd=root,text=True)
def save(p,s):
    f = out/Path(p).name
    f.write_text(s)
    replacements[str(root/p)]=str(f)
def edit(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)

p="internal/checker/checker.go"
s=edit(read(p),"type Checker struct {","""type handlerKey struct {input *Type; mapper *TypeMapper}
type handlerTrace struct {path [48]byte; n int}
func (c *Checker) handlerEvent(event byte) {
    if trace:=c.handlerProbe; trace!=nil && trace.n<len(trace.path) {trace.path[trace.n]=event; trace.n++}
}
type Checker struct {
    handlerProbe *handlerTrace
    handlerSeen map[handlerKey]bool""")
site="links.resolvedType = c.instantiateType(c.getTypeOfSymbol(links.target), links.mapper)"
s=edit(s,site,"""input:=c.getTypeOfSymbol(links.target)
        m:=links.mapper
        if c.handlerProbe==nil && m!=nil && input.flags&TypeFlagsUnion!=0 && input.alias==nil && input.AsUnionType().origin==nil && len(input.Types())==2 {
            _, array := m.data.(*ArrayTypeMapper)
            first,second:=input.Types()[0],input.Types()[1]
            if array && first.flags&TypeFlagsUndefined!=0 && second.flags&TypeFlagsObject!=0 && second.alias!=nil && strings.HasSuffix(second.alias.symbol.Name,"EventHandler") {
                key:=handlerKey{input,m}
                var trace handlerTrace
                c.handlerProbe=&trace
                hit:=c.handlerSeen[key]
                links.resolvedType=c.instantiateType(input,m)
                c.handlerProbe=nil
                if c.handlerSeen==nil || len(c.handlerSeen)>=32768 {c.handlerSeen=make(map[handlerKey]bool)}
                c.handlerSeen[key]=true
                path:=string(trace.path[:trace.n])
                if hit {path="repeat:"+path} else {path="first:"+path}
                v,_:=handlerPaths.LoadOrStore(path,new(atomic.Uint64))
                v.(*atomic.Uint64).Add(1)
                return links.resolvedType
            }
        }
        links.resolvedType=c.instantiateType(input,m)""")
site="func (c *Checker) instantiateTypeWorker(t *Type, m *TypeMapper, alias *TypeAlias) *Type {"
s=edit(s,site,site+"""
    if c.handlerProbe!=nil {
        switch {
        case t.flags&TypeFlagsUnion!=0: c.handlerEvent('U')
        case t.flags&TypeFlagsTypeParameter!=0: c.handlerEvent('P')
        case t.flags&TypeFlagsObject!=0 && t.objectFlags&ObjectFlagsReference!=0: c.handlerEvent('R')
        case t.flags&TypeFlagsObject!=0: c.handlerEvent('O')
        default: c.handlerEvent('?')
        }
    }""")
s=edit(s,"if cachedType, ok := cache[key]; ok {","if cachedType, ok := cache[key]; ok {\n c.handlerEvent('C')")
s=edit(s,"if t, ok := intf.instantiations[id]; ok {","if t, ok := intf.instantiations[id]; ok {\n c.handlerEvent('r')")
site="result := data.instantiations[key]"
s=edit(s,site,site+"\n if result!=nil { c.handlerEvent('h') } else { c.handlerEvent('m') }")
site="return c.getUnionTypeEx(newTypes, UnionReductionLiteral, alias, nil /*origin*/)"
s=edit(s,site,"c.handlerEvent('u')\n"+site)
s+="""
var handlerPaths sync.Map
func HandlerPaths() map[string]uint64 {
    out:=map[string]uint64{}
    handlerPaths.Range(func(k,v any) bool {out[k.(string)]=v.(*atomic.Uint64).Load();return true})
    return out
}
"""
save(p,s)
p="cmd/tsgo/main.go"
s=edit(read(p),'"context"','"context"\n"encoding/json"\n"github.com/microsoft/typescript-go/internal/checker"')
save(p,edit(s,"os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.HandlerPaths()); os.Exit(status)"))
(out/"overlay.json").write_text(json.dumps({"Replace":replacements}))
