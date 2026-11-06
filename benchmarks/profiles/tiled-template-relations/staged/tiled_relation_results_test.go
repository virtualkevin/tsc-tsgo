package checker

import (
	"math/rand/v2"
	"testing"
)

func TestTiledRelationHistory(t *testing.T) {
	for seed := uint64(1); seed <= 24; seed++ {
		rng := rand.New(rand.NewPCG(seed, seed+91))
		var store Relation
		reference := make(map[relationKey]RelationComparisonResult)
		keys := make([]relationKey, 2048)
		for i := range keys {
			keys[i] = relationKey{packed: uint64(rng.IntN(128)+1)<<32 | uint64(rng.IntN(128)+1)<<2 | uint64(rng.IntN(4))}
			if i%11 == 0 {
				keys[i] = relationKey{hash: CacheHashKey{Hi: uint64(i), Lo: rng.Uint64()}}
			}
		}
		for step := 0; step < 16000; step++ {
			key := keys[rng.IntN(len(keys))]
			if step%3 != 0 {
				value := RelationComparisonResultFailed
				if step%5 == 0 {
					value = 0
				}
				if step%7 == 0 {
					value = RelationComparisonResult(rng.Uint32())
				}
				store.set(key, value)
				reference[key] = value
			} else if store.get(key) != reference[key] {
				t.Fatal(seed, step, "value")
			}
			if store.size() != len(reference) {
				t.Fatal(seed, step, "size")
			}
		}
		for key, value := range reference {
			if store.get(key) != value {
				t.Fatal(seed, "final")
			}
		}
		store = Relation{}
		if store.size() != 0 {
			t.Fatal("reset")
		}
	}
}
func originalTiledTestHash(source, target *Type, state IntersectionState, identity, ignore bool) (CacheHashKey, bool) {
	if identity && source.id > target.id {
		source, target = target, source
	}
	var b keyBuilder
	var constrained bool
	if isTypeReferenceWithGenericArguments(source) && isTypeReferenceWithGenericArguments(target) {
		b.writeByte('g')
		constrained = b.writeGenericTypeReferences(source, target, ignore)
	} else {
		b.writeByte('s')
		b.writeType(source)
		b.writeType(target)
	}
	b.writeUint32(uint32(state))
	return b.hash(), constrained
}
func TestTiledRelationKeys(t *testing.T) {
	ids := []TypeId{0, 1, 15, 16, 17, (1 << 30) - 1, 1 << 30, ^TypeId(0)}
	kinds := []TypeFlags{TypeFlagsStringLiteral, TypeFlagsTemplateLiteral, TypeFlagsStringLiteral | TypeFlagsEnumLiteral, TypeFlagsObject}
	hashes := make(map[relationKey]CacheHashKey)
	for _, a := range ids {
		for _, b := range ids {
			for _, kind := range kinds {
				for _, identity := range []bool{false, true} {
					for state := IntersectionState(0); state < 5; state++ {
						if a == b && kind != TypeFlagsTemplateLiteral {
							continue
						} // Live nonzero IDs identify a single type.
						source, target := &Type{id: a, flags: kind}, &Type{id: b, flags: TypeFlagsTemplateLiteral}
						got, constrained := getRelationKey(source, target, state, identity, false)
						hash, wantConstrained := originalTiledTestHash(source, target, state, identity, false)
						if constrained != wantConstrained {
							t.Fatal("constraints")
						}
						if got.packed == 0 {
							if got.hash != hash {
								t.Fatal("fallback hash")
							}
						} else {
							if !got.hash.IsZero() || state > 3 || a == 0 || b == 0 || a >= 1<<30 || b >= 1<<30 {
								t.Fatal("packing domain")
							}
							if prior, ok := hashes[got]; ok && prior != hash {
								t.Fatal("packed collision")
							}
							hashes[got] = hash
						}
						if identity {
							reverse, _ := getRelationKey(target, source, state, true, false)
							if reverse != got {
								t.Fatal("identity ordering")
							}
						}
					}
				}
			}
		}
	}
}
