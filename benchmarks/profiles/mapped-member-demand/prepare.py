"""Observe mapped symbols created under the intersection skip heuristic."""
import json
from pathlib import Path
import subprocess
import sys

here=Path(__file__).resolve().parent
root=here.parents[2]/"packages/tsc-go"
out=Path(sys.argv[1]).resolve()
out.mkdir(parents=True,exist_ok=True)
overlay={}
def edit(file,changes):
    src=subprocess.check_output(["git","show","bd1baea:packages/tsc-go/"+file],cwd=root,text=True)
    for a,b in changes:
        assert src.count(a)==1,a
        src=src.replace(a,b)
    dest=out/Path(file).name
    dest.write_text(src)
    overlay[str(root/file)]=str(dest)
edit("internal/checker/checker.go",[
    ("type Checker struct {","type Checker struct {\n demandDepth int\n mappedDemand *mappedDemandStore"),
    ("addMemberForKeyTypeWorker := func(keyType *Type, propNameType *Type) {",
     "var observedOwner *mappedDemandOwner\n fromKeyof := false\n addMemberForKeyTypeWorker := func(keyType *Type, propNameType *Type) {"),
    ("// We have a { [P in keyof T]: X }\n\t\tc.forEachMappedTypePropertyKeyTypeAndIndexSignatureKeyType(modifiersType, include,",
     "// We have a { [P in keyof T]: X }\n fromKeyof=true\n c.forEachMappedTypePropertyKeyTypeAndIndexSignatureKeyType(modifiersType, include,"),
    ("members[propName] = prop","""members[propName] = prop
    if c.demandDepth!=0 {
        cohort:=0
        if nameType==nil && keyType==propNameType && keyType.flags==TypeFlagsStringLiteral {
            cohort=1
            if fromKeyof {cohort=2}
        }
        c.recordHeuristicMember(&observedOwner,prop,cohort)
    }"""),
    ("c.setStructuredTypeMembers(t, members, nil, nil, indexInfos)\n}\n\nfunc (c *Checker) getTypeOfMappedSymbol", """c.setStructuredTypeMembers(t, members, nil, nil, indexInfos)
    t.AsStructuredType().observedMappedOwner=observedOwner
}

func (c *Checker) getTypeOfMappedSymbol"""),
    ("func (c *Checker) getTypeOfMappedSymbol(symbol *ast.Symbol) *Type {","""func (c *Checker) getTypeOfMappedSymbol(symbol *ast.Symbol) *Type {
        if c.mappedDemand!=nil {
            if entry:=c.mappedDemand.entries[symbol];entry!=nil {entry.flags.Or(1)}
        }""")])
site="resolved := c.resolveStructuredTypeMembers(apparent)"
edit("internal/checker/lazy_properties.go",[(site,"c.demandDepth++\n"+site+"\nc.demandDepth--")])
edit("internal/checker/types.go",[
    ("type StructuredType struct {","type StructuredType struct {\n observedMappedOwner *mappedDemandOwner"),
    ("return t.properties\n}", "if owner:=t.observedMappedOwner;owner!=nil {owner.flags.Or(4)}\n return t.properties\n}"),
    ("return t.members\n}", "if owner:=t.observedMappedOwner;owner!=nil {owner.flags.Or(8)}\n return t.members\n}")])
edit("internal/checker/pending_members.go",[("return t.members[name]\n}", """symbol:=t.members[name]
    if owner:=t.observedMappedOwner;owner!=nil {
        if entry:=owner.entries[symbol];entry!=nil {entry.flags.Or(2)}
    }
    return symbol
}""")])
edit("cmd/tsgo/main.go",[('"context"','"context"\n "encoding/json"\n "github.com/microsoft/typescript-go/internal/checker"'),
    ("os.Exit(runMain())","status:=runMain(); json.NewEncoder(os.Stderr).Encode(checker.MappedDemand()); os.Exit(status)")])
overlay[str(root/"internal/checker/mapped_demand_probe.go")]=str(here/"probe.go.txt")
(out/"overlay.json").write_text(json.dumps({"Replace":overlay}))
