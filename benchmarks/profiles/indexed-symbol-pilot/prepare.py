from pathlib import Path
import difflib,json,hashlib,subprocess
r=Path('/home/dev/tssss/tsc-tsgo');d=Path('/tmp/tsc-indexed-symbol-pilot');base={}
for path in ['packages/tsc-go/internal/ast/symbol.go','packages/tsc-go/internal/binder/binder.go','packages/tsc-go/internal/checker/checker.go']:base[path]=(r/path).read_text()
control=dict(base)
p='packages/tsc-go/internal/ast/symbol.go';assert control[p].count('\tExportSymbol     *Symbol\n')==1
control[p]=control[p].replace('\tExportSymbol     *Symbol\n','\tExportSymbol     *Symbol\n\t// Allocation-only lookup handle, immutable after publication; independent of id.\n\tlinkIndex uint32\n')
for p in ['packages/tsc-go/internal/binder/binder.go','packages/tsc-go/internal/checker/checker.go']:
 assert control[p].count('core.Arena[ast.Symbol]')==1;control[p]=control[p].replace('core.Arena[ast.Symbol]','ast.SymbolAllocator')
for name in ['symbol_allocator.go','symbol_allocator_test.go']:control['packages/tsc-go/internal/ast/'+name]=(d/'handles'/name).read_text()
indexed=dict(control)
p='packages/tsc-go/internal/checker/checker.go';assert indexed[p].count('core.PointerLinkStore[ast.Symbol, ValueSymbolLinks]')==1
indexed[p]=indexed[p].replace('core.PointerLinkStore[ast.Symbol, ValueSymbolLinks]','ast.IndexedSymbolLinks[ValueSymbolLinks]')
for name in ['indexedpointerlinkstore.go','indexedpointerlinkstore_test.go']:indexed['packages/tsc-go/internal/core/'+name]=(d/'indexed'/name).read_text()
indexed['packages/tsc-go/internal/ast/symbol_links.go']=(d/'indexed/symbol_links.go').read_text()
for name,files in [('control',control),('combined',indexed)]:
 replace={}
 for path,text in files.items():
  out=d/name/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(text);replace[str(r/path)]=str(out)
 subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',*replace.values()],check=True)
 for path in files:files[path]=(d/name/path).read_text()
 (d/(name+'-overlay.json')).write_text(json.dumps({'Replace':replace},indent=2)+'\n')
def patch(a,b):
 return ''.join(''.join(difflib.unified_diff(a.get(p,'').splitlines(True),b.get(p,'').splitlines(True),fromfile='a/'+p if p in a else '/dev/null',tofile='b/'+p if p in b else '/dev/null')) for p in sorted(set(a)|set(b)) if a.get(p)!=b.get(p))
for name,a,b in [('handles.patch',base,control),('indexed-over-handles.patch',control,indexed),('indexed-combined.patch',base,indexed)]:
 (d/name).write_text(patch(a,b))
sha=lambda b:hashlib.sha256(b).hexdigest()
metadata={'status':'formatted source draft; tests not yet run','baseRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'mainModified':False,'analysisDocumentSha256':sha((r/'OPTI_ANALYSIS_01.md').read_bytes()),'sourceBasis':{p:sha(t.encode()) for p,t in base.items()},'patches':{p.name:sha(p.read_bytes()) for p in d.glob('*.patch')},'combinedFiles':{p:sha(t.encode()) for p,t in indexed.items()},'variants':['unchanged preserved baseline','same allocation handles, existing PointerLinkStore','same handles plus sparse indexed ValueSymbolLinks'],'notYetDone':['full compiler correctness validation','actual layout/codegen and page occupancy','three-way workload time/RSS and A/A calibration']}
(d/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('Formatted control and combined overlays prepared; main source unchanged.')
