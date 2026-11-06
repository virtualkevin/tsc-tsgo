from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go';st=p/'staged';paths={}
def stage(rel,text):
 f=st/Path(rel).name;f.write_text(text);subprocess.run(['/tmp/tsc-toolchains/go/bin/gofmt','-w',str(f)],check=True);paths[str(m/rel)]=str(f)
s=(m/'internal/checker/checker.go').read_text()
a=s.index('func getRelationKey(');b=s.index('\nfunc getNodeListKey(',a)
old=s[a:b]
new='''func getRelationKey(source *Type, target *Type, intersectionState IntersectionState, isIdentity bool, ignoreConstraints bool) (relationKey, bool) {
 if isIdentity && source.id > target.id { source, target = target, source }
 // Preserve the original generic-detection order and its possible resolutions.
 generic := isTypeReferenceWithGenericArguments(source) && isTypeReferenceWithGenericArguments(target)
 if !generic && target.flags == TypeFlagsTemplateLiteral && (source.flags == TypeFlagsStringLiteral || source.flags == TypeFlagsTemplateLiteral) &&
  source.objectFlags&ObjectFlagsReference == 0 && target.objectFlags&ObjectFlagsReference == 0 &&
  source.id != 0 && target.id != 0 && source.id < 1<<30 && target.id < 1<<30 && intersectionState <= (IntersectionStateSource|IntersectionStateTarget) {
  return relationKey{packed:uint64(source.id)<<32|uint64(target.id)<<2|uint64(intersectionState)},false
 }
 return getHashedRelationKey(source,target,intersectionState,generic,ignoreConstraints)
}

func getHashedRelationKey(source *Type, target *Type, intersectionState IntersectionState, generic bool, ignoreConstraints bool) (relationKey, bool) {
 var b keyBuilder
 var constrained bool
 if generic {
  b.writeByte('g')
  constrained=b.writeGenericTypeReferences(source,target,ignoreConstraints)
 } else {
  b.writeByte('s')
  b.writeType(source)
  b.writeType(target)
 }
 b.writeUint32(uint32(intersectionState))
 return relationKey{hash:b.hash()},constrained
}
'''
stage('internal/checker/checker.go',s[:a]+new+s[b:])
s=(m/'internal/checker/relater.go').read_text()
a=s.index('type Relation struct {');b=s.index('\nfunc (c *Checker) isTypeIdenticalTo',a)
s=s[:a]+'''type Relation struct {
 results map[CacheHashKey]RelationComparisonResult
 packed tiledRelationResults
}
func (r *Relation) get(key relationKey) RelationComparisonResult {
 if key.packed != 0 {return r.packed.get(key.packed)}
 return r.results[key.hash]
}
func (r *Relation) set(key relationKey,result RelationComparisonResult) {
 if key.packed != 0 {r.packed.set(key.packed,result);return}
 if r.results==nil {r.results=make(map[CacheHashKey]RelationComparisonResult)}
 r.results[key.hash]=result
}
func (r *Relation) size() int {return len(r.results)+r.packed.size()}
'''+s[b:]
s=s.replace('maybeKeys      []CacheHashKey','maybeKeys      []relationKey').replace('maybeKeysSet   collections.Set[CacheHashKey]','maybeKeysSet   collections.Set[relationKey]')
stage('internal/checker/relater.go',s)
s=(m/'internal/checker/primitive_union_test.go').read_text();assert s.count('c.assignableRelation.results = nil')==1
stage('internal/checker/primitive_union_test.go',s.replace('c.assignableRelation.results = nil','*c.assignableRelation = Relation{}'))
for name in ['tiled_relation_results.go','tiled_relation_results_test.go','tiled_relation_semantics_test.go']:
 stage('internal/checker/'+name,(st/name).read_text())
(p/'overlay.json').write_text(json.dumps({'Replace':paths},indent=2)+'\n')
(p/'base.json').write_text(json.dumps({str(Path(k).relative_to(m)):hashlib.sha256(Path(k).read_bytes()).hexdigest() for k in paths if Path(k).exists()},indent=2)+'\n')
