from pathlib import Path
import json,difflib,subprocess
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
replace={};patch=[]
def save(rel,s):
 p=root/rel;old=p.read_text();dest=out/'overlay-source'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(s)
 subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',str(dest)],check=True)
 replace[str(p)]=str(dest);patch.extend(difflib.unified_diff(old.splitlines(True),dest.read_text().splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
rel='packages/tsc-go/internal/checker/pending_members.go';s=(root/rel).read_text()
def edit(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b)
edit('\tt.pendingMembers = nil\n\tmembers := p.ownTable()', '\tkind := 0\n\tif p.hasBases { kind = 1 }; if p.resolving { kind = 2 }\n\tobserveMaterialization(kind, len(p.source.entries), len(p.bases))\n\tt.pendingMembers = nil\n\tmembers := p.ownTable()')
edit('if len(properties) != len(members) {\n\t\treturn','if len(properties) != len(members) {\n\t\tobserveMaterialization(3, len(members), len(properties))\n\t\treturn')
edit('if members[symbol.Name] != symbol {\n\t\t\treturn','if members[symbol.Name] != symbol {\n\t\t\tobserveMaterialization(4, len(members), len(properties))\n\t\t\treturn')
edit('if !hasMemberNames(names, properties) {','if !hasMemberNames(names, properties) {\n\t\tobserveMaterialization(5, len(properties), len(p.bases))')
edit('\t\tp.source.lastMemberNames = names\n\t}', '\t\tp.source.lastMemberNames = names\n\t} else { observeMaterialization(6, len(properties), len(p.bases)) }')
edit('func (p *pendingInstantiatedMembers) materializeTable(t *StructuredType) {','func (p *pendingInstantiatedMembers) materializeTable(t *StructuredType) {\n\timmediate := p.memberNames == nil')
edit('\tmembers := make(ast.SymbolTable, len(p.materializedProperties))','\tkind := 8; if immediate { kind = 7 }; observeMaterialization(kind, len(p.materializedProperties), 0)\n\tmembers := make(ast.SymbolTable, len(p.materializedProperties))')
save(rel,s)
rel='packages/tsc-go/cmd/tsgo/main.go';s=(root/rel).read_text();assert '"fmt"' not in s and 'internal/checker"' not in s
s=s.replace('"context"','"context"\n"fmt"\n"github.com/microsoft/typescript-go/internal/checker"');assert s.count('return int(result.Status)')==1
s=s.replace('return int(result.Status)','if err := checker.WriteMaterializationCensus(); err != nil { fmt.Fprintln(os.Stderr, err); return 1 }; return int(result.Status)');save(rel,s)
for src,name in [('census.go','materialization_census.go'),('census_test.go','materialization_census_test.go')]:
 p=root/'packages/tsc-go/internal/checker'/name;assert not p.exists();replace[str(p)]=str(out/src)
(out/'overlay.json').write_text(json.dumps({'Replace':replace},indent=2)+'\n');(out/'instrumentation.patch').write_text(''.join(patch))
