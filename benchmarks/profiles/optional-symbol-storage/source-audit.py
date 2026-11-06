from pathlib import Path
import collections,hashlib,json,subprocess,re
P=Path(__file__).resolve().parent;R=P.parents[2];M=R/'packages/tsc-go'
sha=lambda b:hashlib.sha256(b).hexdigest()
plan=json.loads((P/'migration.json').read_text());sites=plan['Sites']
assert len(sites)==147 and collections.Counter(s['Kind'] for s in sites)==dict(read=131,assignment=11,address=5)
assert len(plan['SourceHashes'])==23
edits=collections.defaultdict(list)
for e in plan['Edits']:edits[e['File']].append(e)
format=lambda data:subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=data)
checked={}
for file,changes in edits.items():
 f=Path(file);original=f.read_bytes();assert sha(original)==plan['SourceHashes'][file]
 changes.sort(key=lambda e:(e['Start'],e['End']))
 for a,b in zip(changes,changes[1:]):assert a['End']<=b['Start']
 expected=original
 for e in reversed(changes):expected=expected[:e['Start']]+e['Text'].encode()+expected[e['End']:]
 relative=f.relative_to(M);candidate=(P/'staged'/relative).read_bytes()
 if str(relative)=='internal/ast/symbol.go':
  text=expected.decode()
  for field in ['Members','Exports','ExportSymbol']:
   matches=[l for l in text.splitlines(True) if l.strip().startswith(field+' ')];assert len(matches)==1;text=text.replace(matches[0],'')
  text=text.replace('\tParent           *Symbol\n','\tParent           *Symbol\n\tcold *symbolCold\n')
  split=candidate.index(b'// symbolCold is allocated only')
  assert candidate[:split].rstrip()==format(text.encode()).rstrip()
  checked[str(relative)]={'before':sha(original),'after':sha(candidate),'scope':'Type-aware accesses and exact field relocation checked; appended implementation requires review and behavioral validation.','implementationSha256':sha(candidate[split:])}
 else:
  assert format(expected)==candidate,str(relative)
  checked[str(relative)]={'before':sha(original),'after':sha(candidate),'scope':'Exact type-aware field-access substitutions only.'}
transform='internal/transformers/declarations/transform.go'
original=(M/transform).read_bytes();assert sha(original)=='3642d191e79150264e99afdadf9a832930c6f4ab2a39257d313e65498e9aa072'
assert original.count(b'node.Symbol.Exports[')==1
assert original.replace(b'node.Symbol.Exports[',b'node.Symbol.ExportsTable()[')==(P/'staged'/transform).read_bytes()
keybuilder=M/'internal/checker/keybuilder.go';assert sha(keybuilder.read_bytes())=='6c50894e0b6c481c2878af208c31f575e15829025a594261cda3e9e10a16d13a'
# Same clone history, with only field/method notation changed, on retained source.
clone=(P/'staged/internal/checker/optional_symbol_clone_test.go').read_text()
for method,field in [('MembersTable','Members'),('ExportsTable','Exports'),('ExportTarget','ExportSymbol')]:clone=clone.replace('.'+method+'()', '.'+field)
clone=re.sub(r'(?m)^(\s*)(\w+)\.Set(Members|Exports|ExportSymbol)\((.*)\)$',r'\1\2.\3 = \4',clone)
assert format(clone.encode())==(P/'baseline/optional_symbol_clone_test.go').read_bytes()
(P/'source-audit.json').write_text(json.dumps({'passed':True,'scope':'Mechanical migration and guarded files; not a proof of new storage implementation or whole-compiler equivalence.','planSha256':sha((P/'migration.json').read_bytes()),'controllerSha256':sha(Path(__file__).read_bytes()),'checkedFiles':checked},indent=2)+'\n')
print('Source migration audit passed for',len(checked),'files')
