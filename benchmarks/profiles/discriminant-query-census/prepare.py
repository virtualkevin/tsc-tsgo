from pathlib import Path
import json,subprocess,hashlib
r=Path('/home/dev/tssss/tsc-tsgo');p=r/'benchmarks/profiles/discriminant-query-census';old=p.parent/'jsx-context-census';m=r/'packages/tsc-go'
s=(old/'staged/jsx_context_census.go').read_text()
s=s.replace('JsxContext','DiscriminantQuery').replace('jsxContext','discriminantQuery').replace('jsxRequest','discriminantRequest').replace('JSX_CONTEXT','DISCRIMINANT_QUERY').replace('JSX census','discriminant query census')
a=s.index('type discriminantRequestKey struct');b=s.index('type discriminantRequestHistory',a)
s=s[:a]+'''type discriminantRequestKey struct { Type TypeId; Name string }
'''+s[b:]
a=s.index('type discriminantQueryBucket struct');b=s.index('type discriminantQueryRow',a)
s=s[:a]+'''type discriminantQueryBucket struct {
 Kind uint8
 TypeFlags TypeFlags
 ObjectFlags ObjectFlags
 ActiveContext bool
}
'''+s[b:]
s=s.replace('\n\tInferenceSitesBefore, InferenceSitesAfter, ChangedInferenceFlags       uint64','')
s=s.replace('\n\tinferenceSites int\n\tinferenceFlags InferenceFlags','')
a=s.index('func (c *Checker) beginDiscriminantQuery(');b=s.index('\n\t_, tracked :=',a)
s=s[:a]+'''func (c *Checker) beginDiscriminantQuery(t *Type, name string, discriminator Discriminator) *discriminantQueryFrame {
 o := c.discriminantQueryCensus
 key := discriminantRequestKey{t.id, name}
 kind := uint8(0)
 switch discriminator.(type) {
 case *TypeDiscriminator: kind = 1
 case *ObjectLiteralDiscriminator: kind = 2
 }
 bucket := discriminantQueryBucket{kind, t.flags, t.objectFlags, c.instantiationDepth != 0 || len(c.activeMappers) != 0}
'''+s[b:]
a=s.index('\n\tif inference != nil');b=s.index('\n\to.active = f',a);s=s[:a]+s[b:]
a=s.index('\n\trow.InferenceSitesBefore');b=s.index('\n}\n',a);s=s[:a]+s[b:]
s=s.replace('"github.com/microsoft/typescript-go/internal/ast"','')
a=s.index('"All checkExpressionWithContextualType');b=s.index('", owners}',a)
s=s[:a]+'''"Only property-or-index queries directly dispatched by discriminateTypeByDiscriminableItems. Aggregates uncapped; first 131072 distinct checker-local type-ID/property-name pairs tracked. Keys deliberately omit mutable context, augmentation state and caller; repetition is not semantic equivalence. Names retained; no Type roots or extra semantic queries. Nested completed observations are subtracted for exclusive work. Counter and assignable/subtype size deltas are incomplete effects; zero does not prove purity. Timings are instrumented, not workload performance'''+s[b:]
s+='''
func (c *Checker) observedDiscriminantQuery(t *Type, name string, discriminator Discriminator) (result *Type) {
 if c.discriminantQueryCensus != nil {
  frame := c.beginDiscriminantQuery(t, name, discriminator)
  defer func() { c.endDiscriminantQuery(frame, result) }()
 }
 return c.getTypeOfPropertyOrIndexSignatureOfType(t, name)
}
'''
(p/'staged/discriminant_query_census.go').write_text(s)
s=(old/'staged/compiler_jsx_context_census.go').read_text().replace('JsxContext','DiscriminantQuery').replace('JSX_CONTEXT','DISCRIMINANT_QUERY').replace('jsx context','discriminant query')
(p/'staged/compiler_discriminant_query_census.go').write_text(s)
changes={}
def stage(rel,s):
 name=('compiler_' if '/compiler/' in rel else '')+Path(rel).name
 dest=p/'staged'/name;dest.write_text(s)
 subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',str(dest)],check=True)
 changes[str(m/rel)]=str(dest)
s=(m/'internal/checker/checker.go').read_text().replace('type Checker struct {','type Checker struct {\n discriminantQueryCensus *discriminantQueryCensus',1).replace('c := &Checker{}','c := &Checker{}\n c.discriminantQueryCensus = newDiscriminantQueryCensus()',1)
stage('internal/checker/checker.go',s)
s=(m/'internal/checker/relater.go').read_text();a='targetType := c.getTypeOfPropertyOrIndexSignatureOfType(types[i], discriminator.name(n))';assert s.count(a)==1;s=s.replace(a,'targetType := c.observedDiscriminantQuery(types[i], discriminator.name(n), discriminator)');stage('internal/checker/relater.go',s)
s=(m/'internal/execute/tsc.go').read_text();a='\n\tstopTracing(sys, tr)\n\n\treturn tsc.CommandLineResult{\n\t\tStatus: result.Status,';assert s.count(a)==1;s=s.replace(a,'\n if err := program.WriteDiscriminantQueryCensus(); err != nil { panic(err) }\n'+a);stage('internal/execute/tsc.go',s)
for rel,name in [('internal/checker/discriminant_query_census.go','discriminant_query_census.go'),('internal/compiler/discriminant_query_census.go','compiler_discriminant_query_census.go')]:stage(rel,(p/'staged'/name).read_text())
(p/'overlay.json').write_text(json.dumps({'Replace':changes},indent=2)+'\n')
(p/'base.json').write_text(json.dumps({k:hashlib.sha256(Path(k).read_bytes()).hexdigest() for k in changes if Path(k).exists()},indent=2)+'\n')
for name in ['build.py','validate.py']:
 s=(old/name).read_text().replace('jsx-context','discriminant-query').replace('JsxContext','DiscriminantQuery')
 (p/name).write_text(s)

for name in ['discriminant_query_census_test.go','discriminant_query_census_api_test.go']:
 stage('internal/checker/'+name,(p/'staged'/name).read_text())
(p/'overlay.json').write_text(json.dumps({'Replace':changes},indent=2)+'\n')
