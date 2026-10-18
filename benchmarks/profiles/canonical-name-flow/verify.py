from pathlib import Path
import collections,hashlib,json
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((out/'inventory.json').read_text());assert r['Packages']==99 and len(r['SourceHashes'])==494
assert sha(out/'inventory.json')==sha('/tmp/canonical-name-flow-repeat.json')
assert not (out/'inventory.stderr').read_bytes() and not Path('/tmp/canonical-name-flow-repeat.stderr').read_bytes()
counts=collections.Counter(s['operation']+':'+s['origin'] for s in r['Sites']);assert dict(counts)==r['Counts'] and len(r['Sites'])==1205
assert len({(s['file'],s['line'],s['column'],s['operation']) for s in r['Sites']})==len(r['Sites'])
for name,digest in r['SourceHashes'].items():assert sha(root/'packages/tsc-go'/name)==digest
assert sum(v for k,v in counts.items() if k.startswith('table-read:'))==111
assert sum(v for k,v in counts.items() if k.startswith('table-write:'))==67
expected=[('internal/binder/nameresolver.go',132,'Resolve','table-read','parameter','moduleExports[name]'),('internal/checker/pending_members.go',327,'getResolvedMember','table-read','parameter','t.members[name]'),('internal/checker/checker.go',21332,'getUnionOrIntersectionProperty','table-read','parameter','cache[name]'),('internal/checker/checker.go',14720,'getExportOfModule','table-read','parameter','c.getExportsOfSymbol(symbol)[nameText]'),('internal/binder/binder.go',194,'declareSymbolEx','table-read','other-identifier','symbolTable[name]')]
for file,line,fn,op,origin,expr in expected:
 assert sum(s['file']==file and s['line']==line and s['function']==fn and s['operation']==op and s['origin']==origin and s['expression']==expr for s in r['Sites'])==1
 assert expr in (root/'packages/tsc-go'/file).read_text().splitlines()[line-1]
assert not (out/'layout.stderr').read_bytes()
layout=json.loads((out/'layout.json').read_text());assert layout['GoVersion']=='go1.26.9' and layout['Arch']=='amd64'
assert layout['Sizes']=={'currentIdentifier':72,'currentSymbol':96,'handle':8,'handleSymbolEntryMirror':16,'proposedIdentifierMirror':64,'proposedSymbolMirror':88,'string':16,'stringSymbolEntryMirror':24}
tmp=root/'packages/tsc-go/_tmpcanonicalnameaudit/main.go';assert sha(tmp)==sha(out/'layout.go');tmp.unlink();tmp.parent.rmdir()
stdlib=Path('/tmp/tsc-toolchains/go/src/unique')
report={'passed':True,'scope':'Auditor count/source/manual-site checks, exact repeat and layout probe only. No compiler optimization, whole-compiler test suite or speedup established.','packages':r['Packages'],'sourceFiles':len(r['SourceHashes']),'sites':len(r['Sites']),'manualSites':expected,'inventorySha256':sha(out/'inventory.json'),'repeatSha256':sha('/tmp/canonical-name-flow-repeat.json'),'auditorSha256':sha(out/'inventory.go'),'layoutProbeSha256':sha(out/'layout.go'),'layoutResultSha256':sha(out/'layout.json'),'goExecutableSha256':sha('/tmp/tsc-toolchains/go/bin/go'),'stdlibSources':{str(stdlib/n):sha(stdlib/n) for n in ['handle.go','canonmap.go','clone.go']},'temporaryLayoutHelperRemoved':True}
(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Verified inventory, source hashes, five manual sites, repeat and layout probe; temporary helper removed')
