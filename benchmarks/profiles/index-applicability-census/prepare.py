from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go';st=p/'staged'
changes={}
def stage(rel,text):
 dest=st/(('compiler_' if '/compiler/' in rel else '')+Path(rel).name);dest.write_text(text)
 subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',str(dest)],check=True)
 changes[str(m/rel)]=str(dest)
s=(m/'internal/checker/checker.go').read_text()
s=s.replace('type Checker struct {','type Checker struct {\n indexApplicabilityCensus *indexApplicabilityCensus',1)
s=s.replace('c := &Checker{}','c := &Checker{}\n c.indexApplicabilityCensus = newIndexApplicabilityCensus()',1)
a='func (c *Checker) isApplicableIndexType(source *Type, target *Type) bool {'
b='''func (c *Checker) isApplicableIndexType(source *Type, target *Type) (observedResult bool) {
 if c.indexApplicabilityCensus != nil {
  frame := c.beginIndexApplicability(source, target)
  defer func() { c.endIndexApplicability(frame, observedResult) }()
 }
'''
assert s.count(a)==1;s=s.replace(a,b)
stage('internal/checker/checker.go',s)
s=(m/'internal/execute/tsc.go').read_text();anchor='\n\tstopTracing(sys, tr)\n\n\treturn tsc.CommandLineResult{\n\t\tStatus: result.Status,'
assert s.count(anchor)==1
s=s.replace(anchor,'\n if err := program.WriteIndexApplicabilityCensus(); err != nil { panic(err) }\n'+anchor)
stage('internal/execute/tsc.go',s)
s=(p.parent/'variable-branch-census/staged/compiler_variable_branch_census.go').read_text().replace('VariableBranch','IndexApplicability').replace('variable branch','index applicability').replace('VARIABLE_BRANCH','INDEX_APPLICABILITY')
stage('internal/compiler/index_applicability_census.go',s)
for name in ['index_applicability_census.go','index_applicability_census_test.go']:
 stage('internal/checker/'+name,(st/name).read_text())
(p/'overlay.json').write_text(json.dumps({'Replace':changes},indent=2)+'\n')
(p/'base.json').write_text(json.dumps({str(Path(k).relative_to(m)):hashlib.sha256(Path(k).read_bytes()).hexdigest() for k in changes if Path(k).exists()},indent=2)+'\n')
