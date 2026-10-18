from pathlib import Path
import json,difflib
root=Path(__file__).resolve().parents[3]; out=Path(__file__).resolve().parent
replacements={};patch=[]
def save(rel,s):
 p=root/rel; original=p.read_text(); target=out/p.name;target.write_text(s); replacements[str(p)]=str(target)
 patch.extend(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
p='packages/tsc-go/internal/checker/checker.go';s=(root/p).read_text()
s=s.replace('type Checker struct {','type Checker struct {\n argumentRequestCounts *argumentRequestCounts',1)
s=s.replace('c := &Checker{}','c := &Checker{}\n c.argumentRequestCounts = newArgumentRequestCounts()',1)
s=s.replace('type CallState struct {','type CallState struct {\n argumentRequests *argumentRequestFrame',1)
s=s.replace('var s CallState\n','var s CallState\n s.argumentRequests = c.argumentRequestCounts.frame()\n',1)
lines=s.splitlines(True)
for i,line in enumerate(lines):
 if 'c.isSignatureApplicable(s.node' in line:
  if '&diags)' in line: lines[i]=line.replace('&diags)', '&diags, nil)')
  else: lines[i]=line.replace('nil /*diagnosticOutput*/)', 'nil /*diagnosticOutput*/, s.argumentRequests)')
s=''.join(lines)
old='func (c *Checker) isSignatureApplicable(node *ast.Node, args []*ast.Node, signature *Signature, relation *Relation, checkMode CheckMode, reportErrors bool, diagnosticOutput *[]*ast.Diagnostic) bool {'
assert old in s;s=s.replace(old,old.replace(') bool {',', observation *argumentRequestFrame) bool {'))
old='\t\t\targType := c.checkExpressionWithContextualType(arg, paramType, nil /*inferenceContext*/, checkMode)';assert s.count(old)==1
s=s.replace(old,'''            var observedKey argumentRequestKey
            var observedBudget uint32
            if observation != nil {
                observedKey = argumentRequestKey{arg, paramType, checkMode, relation, len(c.flowLoopStack), c.resolutionStart, len(c.activeTypeMappersCaches)}
                observedBudget = c.instantiationCount
            }
'''+old+'''
            observation.record(observedKey, argType, observedBudget, c.instantiationCount)''')
save(p,s)
p='packages/tsc-go/cmd/tsgo/main.go';s=(root/p).read_text().replace('"context"','"context"\n"fmt"\n"github.com/microsoft/typescript-go/internal/checker"')
s=s.replace('return int(result.Status)','if err := checker.WriteArgumentRequestCensus(); err != nil {fmt.Fprintln(os.Stderr,err);return 1}\n return int(result.Status)');save(p,s)
for name,target in [('census.go','argument_request_census.go'),('census_test.go','argument_request_census_test.go')]:
 p=root/'packages/tsc-go/internal/checker'/target;assert not p.exists();replacements[str(p)]=str(out/name)
(out/'instrumentation.patch').write_text(''.join(patch));(out/'overlay.json').write_text(json.dumps({'Replace':replacements},indent=2)+'\n')
