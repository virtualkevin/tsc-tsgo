from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go';sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fmt=lambda s:subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=s.encode()).decode()
s=(m/'internal/checker/checker.go').read_text().replace('type Checker struct {','type Checker struct {\n templateRelationDensity *templateRelationDensity',1).replace('c := &Checker{}','c := &Checker{}\n c.templateRelationDensity = newTemplateRelationDensity()',1)
assert fmt(s)==(p/'staged/checker.go').read_text()
s=(m/'internal/checker/relater.go').read_text();a='\t\tr.relation.set(id, RelationComparisonResultFailed|propagatingVarianceFlags)';assert s.count(a)==1
s=s.replace(a,a+'\n if r.c.templateRelationDensity != nil { r.c.observeTemplateFailure(source, target, intersectionState, r.relation, RelationComparisonResultFailed|propagatingVarianceFlags) }')
assert fmt(s)==(p/'staged/relater.go').read_text()
s=(m/'internal/execute/tsc.go').read_text();a='\n\tstopTracing(sys, tr)\n\n\treturn tsc.CommandLineResult{\n\t\tStatus: result.Status,';assert s.count(a)==1
assert fmt(s.replace(a,'\n if err := program.WriteTemplateRelationDensity(); err != nil { panic(err) }\n'+a))==(p/'staged/tsc.go').read_text()
base=json.loads((p/'base.json').read_text());assert all(sha(m/k)==v for k,v in base.items())
paths=json.loads((p/'overlay.json').read_text())['Replace'];assert len(paths)==len(set(paths.values()))==6
(p/'source-audit.json').write_text(json.dumps({'passed':True,'scope':'Exact original checker/relater/CLI code plus observer field, constructor, after-write hook and post-check export. New helpers reviewed/tested separately; not an equivalence proof.','base':base,'sources':{k:sha(v) for k,v in paths.items()},'controllerSha256':sha(__file__)},indent=2)+'\n')
print('Exact three-file observer-hook migration verified')
