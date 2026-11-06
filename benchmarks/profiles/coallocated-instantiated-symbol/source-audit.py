from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;r=p.parents[2];base=r/'packages/tsc-go/internal/checker/checker.go';original=base.read_text();candidate=(p/'staged/checker.go').read_text()
restored=candidate.replace('\n\tinstantiatedSymbolArena                     core.Arena[instantiatedSymbolRecord]','')
restored=restored.replace('result, resultLinks := c.newInstantiatedSymbolRecord(symbol.Flags, symbol.Name)','result := c.newSymbol(symbol.Flags, symbol.Name)')
restored=restored.replace('// Publish the coallocated links at the original insertion point.\n\tc.valueSymbolLinks.Install(result, resultLinks)','// newSymbol allocated a fresh arena slot, and only its fields have been set\n\t// since then: no link entry can exist for this result yet.\n\tresultLinks := c.valueSymbolLinks.New(result)')
assert restored==original
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(base)==json.loads((p/'base.json').read_text())['checkerSha256']
report={'passed':True,'inverseRestoresCheckerExactly':True,'productionCheckerSha256':sha(base),'staged':{f.name:sha(f) for f in sorted((p/'staged').glob('*.go'))},'scope':'Exact inverse of checker field and constructor edits; not a semantic, GC, or whole-compiler proof.'}
(p/'source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('Exact source inverse passed')
