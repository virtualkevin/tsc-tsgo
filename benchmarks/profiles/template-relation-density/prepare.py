from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go';st=p/'staged';changes={}
def stage(rel,text):
 dest=st/(('compiler_' if '/compiler/' in rel else '')+Path(rel).name);dest.write_text(text)
 subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',str(dest)],check=True);changes[str(m/rel)]=str(dest)
s=(m/'internal/checker/checker.go').read_text().replace('type Checker struct {','type Checker struct {\n templateRelationDensity *templateRelationDensity',1).replace('c := &Checker{}','c := &Checker{}\n c.templateRelationDensity = newTemplateRelationDensity()',1)
stage('internal/checker/checker.go',s)
s=(m/'internal/checker/relater.go').read_text();a='\t\tr.relation.set(id, RelationComparisonResultFailed|propagatingVarianceFlags)';assert s.count(a)==1
s=s.replace(a,a+'\n if r.c.templateRelationDensity != nil { r.c.observeTemplateFailure(source, target, intersectionState, r.relation, RelationComparisonResultFailed|propagatingVarianceFlags) }')
stage('internal/checker/relater.go',s)
s=(m/'internal/execute/tsc.go').read_text();a='\n\tstopTracing(sys, tr)\n\n\treturn tsc.CommandLineResult{\n\t\tStatus: result.Status,';assert s.count(a)==1
stage('internal/execute/tsc.go',s.replace(a,'\n if err := program.WriteTemplateRelationDensity(); err != nil { panic(err) }\n'+a))
s=(p.parent/'index-applicability-census/staged/compiler_index_applicability_census.go').read_text().replace('IndexApplicability','TemplateRelationDensity').replace('index applicability','template relation density').replace('INDEX_APPLICABILITY_CENSUS','TEMPLATE_RELATION_DENSITY')
# Existing helper names ended in Census; new API is Density, not DensityCensus.
s=s.replace('WriteTemplateRelationDensityCensus','WriteTemplateRelationDensity')
stage('internal/compiler/template_relation_density.go',s)
for name in ['template_relation_density.go','template_relation_density_test.go']:stage('internal/checker/'+name,(st/name).read_text())
(p/'overlay.json').write_text(json.dumps({'Replace':changes},indent=2)+'\n')
(p/'base.json').write_text(json.dumps({str(Path(k).relative_to(m)):hashlib.sha256(Path(k).read_bytes()).hexdigest() for k in changes if Path(k).exists()},indent=2)+'\n')
