from pathlib import Path
import hashlib,json,subprocess
p=Path(__file__).resolve().parent;r=p.parents[2];m=r/'packages/tsc-go'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fmt=lambda s:subprocess.check_output(['/tmp/tsc-toolchains/go/bin/gofmt'],input=s.encode()).decode()
old=(m/'internal/checker/checker.go').read_text();new=(p/'staged/checker.go').read_text()
a=old.index('func getRelationKey(');b=old.index('\nfunc getNodeListKey(',a)
c=new.index('func getRelationKey(');d=new.index('\nfunc getNodeListKey(',c)
assert old[:a]==new[:c] and old[b:]==new[d:]
# Check the full fallback key construction mechanically against the retained body.
body=old[a:b];begin=body.index('\tvar b keyBuilder')
expected='func getHashedRelationKey(source *Type, target *Type, intersectionState IntersectionState, generic bool, ignoreConstraints bool) (relationKey, bool) {\n'+body[begin:]
expected=expected.replace('if isTypeReferenceWithGenericArguments(source) && isTypeReferenceWithGenericArguments(target) {','if generic {').replace('return b.hash(), constrained','return relationKey{hash: b.hash()}, constrained')
start=new.index('func getHashedRelationKey(',c)
assert fmt(expected).strip()==new[start:d].strip()
old=(m/'internal/checker/relater.go').read_text();new=(p/'staged/relater.go').read_text()
a=old.index('type Relation struct {');b=old.index('\nfunc (c *Checker) isTypeIdenticalTo',a)
c=new.index('type Relation struct {');d=new.index('\nfunc (c *Checker) isTypeIdenticalTo',c)
assert old[:a]==new[:c]
assert old[b:].replace('maybeKeys      []CacheHashKey','maybeKeys      []relationKey').replace('maybeKeysSet   collections.Set[CacheHashKey]','maybeKeysSet   collections.Set[relationKey]')==new[d:]
old=(m/'internal/checker/primitive_union_test.go').read_text()
assert old.replace('c.assignableRelation.results = nil','*c.assignableRelation = Relation{}')==(p/'staged/primitive_union_test.go').read_text()
assert (p/'staged/tiled_relation_semantics_test.go').read_text().replace('[]relationKey','[]CacheHashKey')==(p/'baseline/tiled_relation_semantics_test.go').read_text()
paths=json.loads((p/'overlay.json').read_text())['Replace'];assert len(paths)==len(set(paths.values()))==6
base=json.loads((p/'base.json').read_text());assert all(sha(m/k)==v for k,v in base.items())
assert sha(m/'internal/checker/keybuilder.go')=='6c50894e0b6c481c2878af208c31f575e15829025a594261cda3e9e10a16d13a'
assert sha(m/'internal/transformers/declarations/transform.go')=='3642d191e79150264e99afdadf9a832930c6f4ab2a39257d313e65498e9aa072'
(p/'source-audit.json').write_text(json.dumps({'passed':True,'base':base,'sources':{k:sha(v) for k,v in paths.items()},'controllerSha256':sha(__file__),'scope':'Original relater body unchanged except typed maybe keys; fallback key hashing mechanically preserved; baseline semantic history identical except key type; test reset covers full storage. New tagged classifier and storage are reviewed/tested separately, not formally proved by this audit.'},indent=2)+'\n')
print('Relater flow, fallback hashing, baseline history and guards verified')
