"""Prepare remaining conversion edits in a separate proposal; do not mutate staging."""
from pathlib import Path
import difflib,hashlib,json,re,subprocess
out=Path(__file__).resolve().parent
stage=out/'staged'
proposal=out/'boundary-proposal'
freeze=json.loads((out/'refinement-freeze-02.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
texts={}
for rel in ['internal/binder/binder.go','internal/checker/checker.go','internal/checker/services.go','internal/checker/nodebuilderimpl.go','internal/checker/relater.go','internal/checker/pending_members.go','internal/checker/types.go']:
 base=stage/rel if (stage/rel).exists() else out.parents[2]/'packages/tsc-go'/rel
 if rel in freeze['sources']:assert sha(base)==freeze['sources'][rel]
 texts[rel]=base.read_text()
def function(text,name,edit):
 match=re.search(r'^func [^\n]*\b'+re.escape(name)+r'\(',text,re.M);assert match,name
 start=match.start();end=text.find('\nfunc ',start+1)
 if end<0:end=len(text)
 return text[:start]+edit(text[start:end])+text[end:]
def replace_once(text,old,new):
 assert text.count(old)==1,(old,text.count(old))
 return text.replace(old,new,1)
binder=texts['internal/binder/binder.go']
def commonjs(s):
 s=replace_once(s,'locals := ast.GetLocals(b.file.AsNode())','locals := ast.GetLocals(b.file.AsNode())\n nameKey := ast.MakeName(name)')
 s=s.replace('ast.MakeName(name)]','nameKey]').replace('b.newSymbol(ast.SymbolFlagsFunctionScopedVariable|ast.SymbolFlagsModuleExports, name)','b.newSymbolKey(ast.SymbolFlagsFunctionScopedVariable|ast.SymbolFlagsModuleExports, nameKey)')
 return s
binder=function(binder,'declareCommonJSVariable',commonjs)
texts['internal/binder/binder.go']=binder
checker=texts['internal/checker/checker.go']
checker=function(checker,'addUndefinedToGlobalsOrErrorOnRedeclaration',lambda s:s.replace('c.globals[ast.MakeName(name)]','c.globals[c.undefinedSymbol.Name]'))
def iteration(s):
 s=replace_once(s,'method := c.getPropertyOfType(t, methodName)','methodNameKey := ast.MakeName(methodName)\n method := c.getPropertyOfTypeKey(t, methodNameKey)')
 return s.replace('ast.MakeName(methodName)]','methodNameKey]')
checker=function(checker,'getIterationTypesOfMethod',iteration)
def private(s):
 s=replace_once(s,'name := binder.GetSymbolNameForPrivateIdentifier(symbol, propName)','nameKey := ast.MakeName(binder.GetSymbolNameForPrivateIdentifier(symbol, propName))')
 return s.replace('ast.MakeName(name)]','nameKey]')
checker=function(checker,'lookupSymbolForPrivateIdentifierDeclaration',private)
def late(s):
 s=replace_once(s,'memberName := getPropertyNameFromType(t)','memberName := getPropertyNameFromType(t)\n memberNameKey := ast.MakeName(memberName)')
 s=s.replace('ast.MakeName(memberName)]','memberNameKey]').replace('c.newSymbolEx(ast.SymbolFlagsNone, memberName, ast.CheckFlagsLate)','c.newSymbolExKey(ast.SymbolFlagsNone, memberNameKey, ast.CheckFlagsLate)')
 return s
checker=function(checker,'lateBindMember',late)
def mapped(s):
 s=replace_once(s,'propName := getPropertyNameFromType(propNameType)','propName := getPropertyNameFromType(propNameType)\n propNameKey := ast.MakeName(propName)')
 s=s.replace('ast.MakeName(propName)]','propNameKey]').replace('c.newSymbol(ast.SymbolFlagsProperty|core.IfElse(isOptional, ast.SymbolFlagsOptional, 0), propName)','c.newSymbolKey(ast.SymbolFlagsProperty|core.IfElse(isOptional, ast.SymbolFlagsOptional, 0), propNameKey)')
 return s
checker=function(checker,'resolveMappedTypeMembers',mapped)
def indexed(s):
 s=replace_once(s,'var propName string','var propName string\n var propNameKey ast.Name')
 s=replace_once(s,'if hasPropName {\n\t\tif accessFlags', 'if hasPropName {\n propNameKey = ast.MakeName(propName)\n\t\tif accessFlags')
 return s.replace('c.getPropertyOfType(objectType, propName)','c.getPropertyOfTypeKey(objectType, propNameKey)').replace('ast.MakeName(propName)]','propNameKey]')
checker=function(checker,'getPropertyTypeForIndexType',indexed)
checker,n=re.subn(r'(patternAmbientModuleAugmentations\s+)ast.SymbolTable',r'\1map[string]*ast.Symbol',checker);assert n==1
checker=replace_once(checker,'ast.GetSymbolTable(&c.patternAmbientModuleAugmentations)[moduleName.NameKey()] = merged','if c.patternAmbientModuleAugmentations == nil { c.patternAmbientModuleAugmentations = make(map[string]*ast.Symbol) }\n c.patternAmbientModuleAugmentations[moduleName.Text()] = merged')
checker=replace_once(checker,'c.patternAmbientModuleAugmentations[ast.MakeName(moduleReference)]','c.patternAmbientModuleAugmentations[moduleReference]')
checker=replace_once(checker,'type ExportCollisionTable = map[string]*ExportCollision','type ExportCollisionTable = map[ast.Name]*ExportCollision')
checker=checker.replace('typeOnlyExportStarMap map[string]*ast.Node','typeOnlyExportStarMap map[ast.Name]*ast.Node')
checker=checker.replace('typeOnlyExportStarMap = make(map[string]*ast.Node)','typeOnlyExportStarMap = make(map[ast.Name]*ast.Node)')
checker=checker.replace('typeOnlyExportStarMap[name.String()]','typeOnlyExportStarMap[name]')
checker=checker.replace('typeOnlyExportStarMap[nameText]','typeOnlyExportStarMap[nameKey]')
checker=checker.replace('typeOnlyExportStarMap[name] != nil','typeOnlyExportStarMap[nameKey] != nil')
checker=checker.replace('nonTypeOnlyNames := collections.NewSetWithSizeHint[string]', 'nonTypeOnlyNames := collections.NewSetWithSizeHint[ast.Name]')
checker=checker.replace('nonTypeOnlyNames.Add(name.String())','nonTypeOnlyNames.Add(name)')
checker=checker.replace('id == ast.InternalSymbolNameExportEquals || len(s.exportsWithDuplicate) == 0 || symbols[ast.MakeName(id)] != nil','id == ast.CanonicalName364445db1828() || len(s.exportsWithDuplicate) == 0 || symbols[id] != nil')
checker=checker.replace('s.specifierText, id))','s.specifierText, id.String()))')
checker=checker.replace('lookupTable[id.String()]','lookupTable[id]')
checker=function(checker,'getPropertyOfTypeExKey',lambda s:s.replace('name := nameKey.String()\n',''))
texts['internal/checker/types.go']=replace_once(texts['internal/checker/types.go'],'typeOnlyExportStarMap map[string]*ast.Node','typeOnlyExportStarMap map[ast.Name]*ast.Node')
texts['internal/checker/checker.go']=checker
# Restore comments moved into empty String calls by the initial AST rewrite.
services=texts['internal/checker/services.go']
services=replace_once(services, 'id := symbol.Name.String(\n', 'id := symbol.Name\n')
services=replace_once(services, '\t\t\t)\n\n\t\t\tif _, ok := symbols[ast.MakeName(id)]', '\n\t\t\tif _, ok := symbols[id]')
services=services.replace('symbols[ast.MakeName(id)] = symbol','symbols[id] = symbol')
texts['internal/checker/services.go']=services
nodebuilder=texts['internal/checker/nodebuilderimpl.go']
nodebuilder=replace_once(nodebuilder, 'return ast.EscapeInternalSymbolName(symbol.Name.String(\n\n\t// The full set of type parameters for a generic class or interface type consists of its outer type parameters plus\n\t// its locally declared type parameters.\n\t))\n}', 'return ast.EscapeInternalSymbolName(symbol.Name.String())\n}\n\n// The full set of type parameters for a generic class or interface type consists of its outer type parameters plus\n// its locally declared type parameters.')
texts['internal/checker/nodebuilderimpl.go']=nodebuilder
relater=texts['internal/checker/relater.go']
relater=replace_once(relater,'excludedProperties.Add(sourceProperty.Name.String(\n\n\t\t// Build the cartesian product\n\t\t))\n\t}', 'excludedProperties.Add(sourceProperty.Name.String())\n\t}\n\n\t// Build the cartesian product')
texts['internal/checker/relater.go']=relater
pending=texts['internal/checker/pending_members.go']
pending=replace_once(pending,'if c.isNamedMember(symbol, symbol.Name.String(\n\t\t// An alias can be replaced by an inherited value. Keep such tables eager.\n\t\t)) {\n', 'if c.isNamedMember(symbol, symbol.Name.String()) {\n\t\t\t// An alias can be replaced by an inherited value. Keep such tables eager.')
texts['internal/checker/pending_members.go']=pending
for rel in texts:
 texts[rel]=re.sub(r'\bast\.\s*\n\s*', 'ast.', texts[rel])
patch=[]
for rel,text in texts.items():
 formatted=subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=text.encode()).decode()
 destination=proposal/rel;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(formatted)
 patch.extend(difflib.unified_diff((stage/rel if (stage/rel).exists() else out.parents[2]/'packages/tsc-go'/rel).read_text().splitlines(True),formatted.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(out/'boundary-proposal.patch').write_text(''.join(patch))
report={'scope':'Prepared follow-up diff against frozen staging; not applied, compiled, tested or timed.','freezeSha256':sha(out/'refinement-freeze-02.json'),'patchSha256':sha(out/'boundary-proposal.patch'),'proposedSources':{rel:sha(proposal/rel) for rel in texts}}
(out/'boundary-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(sha(stage/rel)==freeze['sources'][rel] for rel in texts if rel in freeze['sources'])
print('Prepared',len(texts),'file boundary proposal; frozen staging unchanged')
