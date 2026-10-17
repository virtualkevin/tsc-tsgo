from pathlib import Path
import subprocess,difflib,hashlib,json
root=Path('/home/dev/tssss/tsc-tsgo');out=Path('/tmp/tsc-semantic-census-draft');rev='e94bc1f0dd96ac097f1941144df7fb46e6b86fb7'
def load(path):return subprocess.check_output(['git','show',rev+':'+path],cwd=root).decode()
def one(s,old,new):
 assert s.count(old)==1,old[:100]
 return s.replace(old,new)
checker='packages/tsc-go/internal/checker/checker.go';a=load(checker);b=a
b=one(b,'\ttracer *Tracer // Optional tracer for trace events and type recording (for --generateTrace)','\ttracer *Tracer // Optional tracer for trace events and type recording (for --generateTrace)\n\tcensus *semanticCensus // Diagnostic draft only; never a benchmark compiler.')
b=one(b,'\tc.id = nextCheckerID.Add(1)','\tc.id = nextCheckerID.Add(1)\n\tc.census = newSemanticCensus(c.id)')
for needle in ['\t\tc.diagnostics.Add(diagnostic)','\t\tc.suggestionDiagnostics.Add(diagnostic)']:
 b=one(b,needle,'\t\tif c.census != nil { c.census.diagnostics++ }\n'+needle)
# Record only the actual resolution path after the normal signature-cache hit.
b=one(b,'\tsaveResolutionStart := c.resolutionStart','''\tvar census *censusSpan
\tif c.census != nil {
\t\tcensus = c.beginCensus(censusKey{family:"resolved-signature-miss",node:node,mode:uint32(checkMode),candidates:candidatesOutArray!=nil,resolving:cached==c.resolvingSignature})
\t\tdefer census.finish(c)
\t}
\tsaveResolutionStart := c.resolutionStart''')
needle='\treturn result\n}\n\nfunc (c *Checker) resolveSignature('
b=one(b,needle,'\tif census != nil { census.returnedNormally=true; census.deferred=result==c.resolvingSignature }\n'+needle)
needle='''\tif links.resolvedSignature != nil {
\t\treturn links.resolvedSignature
\t}
\tvar parameters []*ast.Symbol'''
b=one(b,needle,'''\tif links.resolvedSignature != nil {
\t\treturn links.resolvedSignature
\t}
\tvar census *censusSpan
\tif c.census != nil { census=c.beginCensus(censusKey{family:"signature-construction-miss",node:declaration});defer census.finish(c) }
\tvar parameters []*ast.Symbol''')
needle='\treturn links.resolvedSignature\n}\n\nfunc (c *Checker) getTypeParametersFromDeclaration('
b=one(b,needle,'\tif census != nil {census.returnedNormally=true}\n'+needle)
needle='''func (c *Checker) getDeclaredTypeOfClassOrInterface(symbol *ast.Symbol) *Type {
\tlinks := c.declaredTypeLinks.Get(symbol)
\tif links.declaredType == nil {'''
b=one(b,needle,needle+'''
\t\tvar census *censusSpan
\t\tif c.census != nil {census=c.beginCensus(censusKey{family:"class-interface-construction-miss",node:censusSymbolOrigin(symbol),symbol:symbol});defer census.finish(c)}''')
needle='''\t\t\td.target = t
\t\t}
\t}
\treturn links.declaredType'''
b=one(b,needle,'''\t\t\td.target = t
\t\t}
\t\tif census != nil {census.returnedNormally=true}
\t}
\treturn links.declaredType''')
needle='\tif c.instantiationDepth == 100 || c.instantiationCount >= 5_000_000 {'
b=one(b,needle,needle+'\n\t\tif c.census != nil {c.census.budgetRejections++}')
needle='\tc.TotalInstantiationCount++\n\tc.instantiationCount++'
b=one(b,needle,'''\tvar census *censusSpan
\tif c.census != nil {census=c.beginCensus(censusKey{family:"type-instantiation-miss",node:censusSymbolOrigin(t.symbol),typ:t,mapper:m,alias:alias});defer census.finish(c)}
'''+needle)
needle='\tc.instantiationDepth--\n\treturn result\n}\n\nfunc (c *Checker) pushActiveMapper('
b=one(b,needle,'\tc.instantiationDepth--\n\tif census != nil {census.returnedNormally=true;census.errorResult=result==c.errorType}\n\treturn result\n}\n\nfunc (c *Checker) pushActiveMapper(')
main='packages/tsc-go/cmd/tsgo/main.go';ma=load(main);mb=ma
mb=one(mb,'\t"context"','\t"context"\n\t"fmt"\n\t"strings"')
mb=one(mb,'\t"github.com/microsoft/typescript-go/internal/core"','\t"github.com/microsoft/typescript-go/internal/checker"\n\t"github.com/microsoft/typescript-go/internal/core"')
mb=one(mb,'\targs := os.Args[1:]','''\targs := os.Args[1:]
\tif os.Getenv("TSC_GO_CENSUS") != "" {
\t\tfor _, arg := range args {
\t\t\tif !strings.HasPrefix(arg,"-") {continue}
\t\t\tswitch strings.ToLower(strings.TrimLeft(strings.SplitN(arg,"=",2)[0],"-")) {
\t\t\tcase "api", "lsp", "w", "watch", "b", "build":
\t\t\t\tfmt.Fprintln(os.Stderr,"semantic census supports ordinary one-shot CLI compilation only")
\t\t\t\treturn 1
\t\t\t}
\t\t}
\t}''')
mb=one(mb,'\treturn int(result.Status)','\tif err:=checker.FlushSemanticCensus();err!=nil {fmt.Fprintln(os.Stderr,err);return 1}\n\treturn int(result.Status)')
new='packages/tsc-go/internal/checker/semantic_census.go';data=(out/'semantic_census.go').read_text()
files=[(checker,a,b),(main,ma,mb),(new,'',data),('packages/tsc-go/internal/checker/semantic_census_test.go','',(out/'semantic_census_test.go').read_text())]
patch=''.join(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+path if before else '/dev/null',tofile='b/'+path)) for path,before,after in files)
(out/'semantic-census.patch').write_text(patch)
(out/'draft.json').write_text(json.dumps({'status':'unapplied-unbuilt-unvalidated','baselineRevision':rev,'baselineSourceSha256':'78b76607d79c501f3c35fcbbec5a880561699244c7d65daab6f27f42b22f9337','patchSha256':hashlib.sha256(patch.encode()).hexdigest(),'files':[{'path':p,'beforeSha256':hashlib.sha256(a.encode()).hexdigest() if a else None,'afterSha256':hashlib.sha256(b.encode()).hexdigest()} for p,a,b in files]},indent=2)+'\n')
print('Prepared diagnostic-only patch:',len(patch),'bytes')
