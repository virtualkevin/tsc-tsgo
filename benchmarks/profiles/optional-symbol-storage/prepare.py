from pathlib import Path
import json,hashlib,collections,subprocess
P=Path(__file__).resolve().parent;R=P.parents[2];M=R/'packages/tsc-go'
sha=lambda b:hashlib.sha256(b).hexdigest()
plan=json.loads((P/'migration.json').read_text());assert len(plan['Sites'])==147
assert not any(s['Kind'] in ['literal','complex-assignment'] for s in plan['Sites'])
edits=collections.defaultdict(list)
for e in plan['Edits']:edits[e['File']].append(e)
overlay={};base={}
for file,changes in edits.items():
 f=Path(file);data=f.read_bytes();assert sha(data)==plan['SourceHashes'][file]
 changes.sort(key=lambda e:(e['Start'],e['End']))
 for a,b in zip(changes,changes[1:]):assert a['End']<=b['Start'],(a,b)
 for e in reversed(changes):data=data[:e['Start']]+e['Text'].encode()+data[e['End']:]
 relative=f.relative_to(M);target=P/'staged'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 overlay[file]=str(target);base[str(relative)]=sha(f.read_bytes())
f=P/'staged/internal/ast/symbol.go';s=f.read_text()
for name in ['Members','Exports','ExportSymbol']:
 lines=[l for l in s.splitlines(True) if l.strip().startswith(name+' ')]
 assert len(lines)==1,name;s=s.replace(lines[0],'')
s=s.replace('\tParent           *Symbol\n','\tParent           *Symbol\n\tcold *symbolCold\n')
assert 'cold *symbolCold' in s
s+='''
// symbolCold is allocated only when an optional field needs storage. Once
// allocated it is never replaced: pointers returned by table slots remain valid.
type symbolCold struct {
 members SymbolTable
 exports SymbolTable
 exportSymbol *Symbol
}

func (s *Symbol) ensureCold() *symbolCold {
 if s.cold == nil { s.cold = &symbolCold{} }
 return s.cold
}
func (s *Symbol) MembersTable() SymbolTable {
 if s.cold == nil { return nil }; return s.cold.members
}
func (s *Symbol) ExportsTable() SymbolTable {
 if s.cold == nil { return nil }; return s.cold.exports
}
func (s *Symbol) ExportTarget() *Symbol {
 if s.cold == nil { return nil }; return s.cold.exportSymbol
}
func (s *Symbol) SetMembers(value SymbolTable) {
 if s.cold == nil && value == nil { return }
 s.ensureCold().members = value
}
func (s *Symbol) SetExports(value SymbolTable) {
 if s.cold == nil && value == nil { return }
 s.ensureCold().exports = value
}
func (s *Symbol) SetExportSymbol(value *Symbol) {
 if s.cold == nil && value == nil { return }
 s.ensureCold().exportSymbol = value
}
func (s *Symbol) MembersSlot() *SymbolTable { return &s.ensureCold().members }
func (s *Symbol) ExportsSlot() *SymbolTable { return &s.ensureCold().exports }
'''
f.write_text(s)
subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',*overlay.values()],check=True)
for relative in ['internal/ast/optional_symbol_test.go','internal/checker/optional_symbol_clone_test.go']:
 target=P/'staged'/relative
 if target.exists():overlay[str(M/relative)]=str(target)
(P/'overlay.json').write_text(json.dumps({'Replace':overlay},indent=2)+'\n')
(P/'base.json').write_text(json.dumps(base,indent=2)+'\n')
print('Staged',len(overlay),'files; production source unchanged')
