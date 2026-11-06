from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fmt=lambda s:subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=s.encode()).decode()
s=(m/'internal/checker/checker.go').read_text()
s=s.replace('type Checker struct {','type Checker struct {\n indexApplicabilityCensus *indexApplicabilityCensus',1)
s=s.replace('c := &Checker{}','c := &Checker{}\n c.indexApplicabilityCensus = newIndexApplicabilityCensus()',1)
s=s.replace('func (c *Checker) isApplicableIndexType(source *Type, target *Type) bool {','''func (c *Checker) isApplicableIndexType(source *Type, target *Type) (observedResult bool) {
 if c.indexApplicabilityCensus != nil {
  frame := c.beginIndexApplicability(source, target)
  defer func() { c.endIndexApplicability(frame, observedResult) }()
 }
''',1)
assert fmt(s)==(p/'staged/checker.go').read_text()
s=(m/'internal/execute/tsc.go').read_text();a='\n\tstopTracing(sys, tr)\n\n\treturn tsc.CommandLineResult{\n\t\tStatus: result.Status,'
assert s.count(a)==1
s=s.replace(a,'\n if err := program.WriteIndexApplicabilityCensus(); err != nil { panic(err) }\n'+a)
assert fmt(s)==(p/'staged/tsc.go').read_text()
base=json.loads((p/'base.json').read_text());assert all(sha(m/k)==v for k,v in base.items())
paths=json.loads((p/'overlay.json').read_text())['Replace'];assert len(paths)==len(set(paths.values()))==5
assert {str(Path(k).relative_to(m)) for k in paths}=={'internal/checker/checker.go','internal/execute/tsc.go','internal/compiler/index_applicability_census.go','internal/checker/index_applicability_census.go','internal/checker/index_applicability_census_test.go'}
(p/'source-audit.json').write_text(json.dumps({'passed':True,'scope':'Exact original checker expression/call order retained, plus one checker field, constructor hook, named-return observer wrapper, and post-checking export. New observer/compiler helper are reviewed/tested, not proved by this mechanical audit.','base':base,'sources':{k:sha(v) for k,v in paths.items()},'controllerSha256':sha(__file__)},indent=2)+'\n')
print('Exact two-file hook migration verified')
