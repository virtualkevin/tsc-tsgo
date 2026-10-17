package checker

import "testing"

// The pre-packing implementation is the equivalence-class oracle: changing key
// representation must neither merge distinct comparisons nor split normalized
// generic comparisons. It intentionally retains the original byte serialization.
func legacyRelationHash(source, target *Type, state IntersectionState, identity, ignoreConstraints bool) (CacheHashKey, bool) {
	if identity && source.id > target.id {
		source, target = target, source
	}
	var b keyBuilder
	var constrained bool
	if isTypeReferenceWithGenericArguments(source) && isTypeReferenceWithGenericArguments(target) {
		b.writeByte('g')
		constrained = b.writeGenericTypeReferences(source, target, ignoreConstraints)
	} else {
		b.writeByte('s')
		b.writeType(source)
		b.writeType(target)
	}
	hashWrite32(&b.h, state)
	return b.hash(), constrained
}

func TestRelationKeysOrdinaryBoundariesMatchLegacy(t *testing.T) {
	c := &Checker{}
	ids := []TypeId{0, 1, 2, (1 << 30) - 1, 1 << 30, 1 << 31, ^TypeId(0)}
	states := []IntersectionState{0, 1, 2, 3, 4, ^IntersectionState(0)}
	forward := make(map[CacheHashKey]RelationKey)
	reverse := make(map[RelationKey]CacheHashKey)
	for _, sourceID := range ids {
		for _, targetID := range ids {
			for _, state := range states {
				for _, identity := range []bool{false, true} {
					for _, ignoreConstraints := range []bool{false, true} {
						source, target := &Type{id: sourceID}, &Type{id: targetID}
						old, oldConstrained := legacyRelationHash(source, target, state, identity, ignoreConstraints)
						key, constrained := c.getRelationKey(source, target, state, identity, ignoreConstraints)
						if constrained != oldConstrained || key == 0 {
							t.Fatal("ordinary relation changed constraint status or produced reserved zero key")
						}
						if previous, ok := forward[old]; ok && previous != key {
							t.Fatal("one legacy comparison acquired two numeric keys")
						}
						if previous, ok := reverse[key]; ok && previous != old {
							t.Fatalf("distinct comparisons collided: source=%d target=%d state=%d identity=%v", sourceID, targetID, state, identity)
						}
						forward[old], reverse[key] = key, old
						wantFallback := sourceID == 0 || targetID == 0 || sourceID >= 1<<30 || targetID >= 1<<30 || state > 3
						if (key&relationKeyFallbackTag != 0) != wantFallback {
							t.Fatal("invalid packing range or fallback tag")
						}
					}
				}
			}
		}
	}
	// The two identity orientations share a key, but Source/Target state bits do
	// not swap: this is the pre-existing identity normalization contract.
	a, b := &Type{id: 17}, &Type{id: 29}
	key, _ := c.getRelationKey(a, b, IntersectionStateSource, true, false)
	reversed, _ := c.getRelationKey(b, a, IntersectionStateSource, true, false)
	otherState, _ := c.getRelationKey(b, a, IntersectionStateTarget, true, false)
	if key != reversed || key == otherState {
		t.Fatal("identity normalization changed intersection-state meaning")
	}
}

func relationKeyReference(c *Checker, target *Type, args ...*Type) *Type {
	t := c.newObjectType(ObjectFlagsReference, nil)
	t.AsTypeReference().target = target
	t.AsTypeReference().resolvedTypeArguments = args
	return t
}

func TestRelationKeysGenericNormalizationMatchesLegacy(t *testing.T) {
	c := lazyPropertyTestChecker()
	c.noConstraintType = c.newIntrinsicType(TypeFlagsAny, "no constraint")
	c.circularConstraintType = c.newIntrinsicType(TypeFlagsAny, "circular constraint")
	parameter := func(constraint *Type) *Type {
		p := c.newTypeParameter(nil)
		p.AsTypeParameter().constraint = constraint
		p.AsTypeParameter().resolvedBaseConstraint = constraint
		return p
	}
	p, q := parameter(c.noConstraintType), parameter(c.noConstraintType)
	r, s := parameter(c.stringType), parameter(c.stringType)
	target := lazyObject(c)
	otherTarget := lazyObject(c)
	ref := func(args ...*Type) *Type { return relationKeyReference(c, target, args...) }
	pq, qp, pp, qq := ref(p, q), ref(q, p), ref(p, p), ref(q, q)
	constrainedR, constrainedS := ref(r), ref(s)
	types := []*Type{pq, qp, pp, qq, ref(p), ref(q), constrainedR, constrainedS, ref(c.stringType), relationKeyReference(c, otherTarget, p)}
	left, right := p, q
	for range 6 {
		left, right = ref(left), ref(right)
		types = append(types, left, right)
	}
	forward := make(map[CacheHashKey]RelationKey)
	reverse := make(map[RelationKey]CacheHashKey)
	for _, source := range types {
		for _, target := range types {
			for state := IntersectionStateNone; state <= 3; state++ {
				for _, identity := range []bool{false, true} {
					for _, ignoreConstraints := range []bool{false, true} {
						old, oldConstrained := legacyRelationHash(source, target, state, identity, ignoreConstraints)
						key, constrained := c.getRelationKey(source, target, state, identity, ignoreConstraints)
						if constrained != oldConstrained {
							t.Fatal("generic relation lost constrained/broadest distinction")
						}
						if previous, ok := forward[old]; ok && previous != key {
							t.Fatal("normalized relation split")
						}
						if previous, ok := reverse[key]; ok && previous != old {
							t.Fatal("distinct generic relations merged")
						}
						forward[old], reverse[key] = key, old
					}
				}
			}
		}
	}
	first, _ := c.getRelationKey(pp, pp, 0, false, false)
	alpha, _ := c.getRelationKey(qq, qq, 0, false, false)
	distinct, _ := c.getRelationKey(pq, pp, 0, false, false)
	if first != alpha || first == distinct {
		t.Fatal("type-parameter occurrence positions lost alpha-equivalence")
	}
	narrow, constrained := c.getRelationKey(constrainedR, constrainedR, 0, false, false)
	broad, broadConstrained := c.getRelationKey(constrainedR, constrainedR, 0, false, true)
	if !constrained || broadConstrained || narrow == broad {
		t.Fatal("constraint normalization lost broadest recursion key")
	}
	otherNarrow, _ := c.getRelationKey(constrainedS, constrainedS, 0, false, false)
	otherBroad, _ := c.getRelationKey(constrainedS, constrainedS, 0, false, true)
	if narrow == otherNarrow || broad != otherBroad {
		t.Fatal("constrained parameters were normalized too early")
	}
	if broad&relationKeyFallbackTag == 0 {
		t.Fatal("generic relation was packed using reference IDs")
	}
}

func TestRelationKeyFallbackUsesAllHashBitsAndCheckerLifetime(t *testing.T) {
	c := &Checker{}
	a, b := &Type{id: 1}, &Type{id: 2}
	packed, _ := c.getRelationKey(a, b, 0, false, false)
	if c.relationKeyIds != nil {
		t.Fatal("ordinary relation allocated fallback storage")
	}
	hashes := []CacheHashKey{{}, {Lo: 1}, {Hi: 1}, {Lo: 1, Hi: 1}, {Lo: 1, Hi: 1 << 63}}
	seen := map[RelationKey]bool{packed: true}
	for _, hash := range hashes {
		key := c.internRelationHash(hash)
		if seen[key] || key&relationKeyFallbackTag == 0 || c.internRelationHash(hash) != key {
			t.Fatal("fallback key collided or changed")
		}
		seen[key] = true
	}
	other := &Checker{}
	other.internRelationHash(CacheHashKey{Lo: 99})
	otherKey := other.internRelationHash(hashes[0])
	if c.internRelationHash(hashes[0]) == otherKey || len(c.relationKeyIds) != len(hashes) {
		t.Fatal("checker fallback interner was shared")
	}
	// Exhaustion must never wrap onto an existing packed or fallback key.
	c.relationKeyCount = uint64(relationKeyFallbackTag) - 1
	if c.internRelationHash(hashes[0]) == 0 {
		t.Fatal("existing key unavailable at exhaustion")
	}
	defer func() {
		if recover() == nil {
			t.Fatal("fallback counter wrapped")
		}
	}()
	c.internRelationHash(CacheHashKey{Hi: 99})
}

func TestRelationKeysPreserveMaybeStackCacheFlagsAndSize(t *testing.T) {
	c := &Checker{}
	c.identityRelation = &Relation{}
	relation := &Relation{}
	ordinary, _ := c.getRelationKey(&Type{id: 1}, &Type{id: 2}, 0, false, false)
	fallback := c.internRelationHash(CacheHashKey{Hi: 42})
	// Probe-only interned keys must not consume the relation's complexity budget.
	c.internRelationHash(CacheHashKey{Hi: 43})
	if relation.size() != 0 {
		t.Fatal("interned keys changed relation size")
	}
	r := c.getRelater()
	r.relation, r.relationCount = relation, 10
	r.maybeKeys = append(r.maybeKeys, ordinary, fallback)
	r.maybeKeysSet.Add(ordinary)
	r.maybeKeysSet.Add(fallback)
	r.resetMaybeStack(1, RelationComparisonResultReportsUnreliable, true)
	if relation.size() != 1 || r.relationCount != 9 || !r.maybeKeysSet.Has(ordinary) || r.maybeKeysSet.Has(fallback) {
		t.Fatal("partial maybe-stack commit changed accounting")
	}
	if relation.get(fallback) != RelationComparisonResultSucceeded|RelationComparisonResultReportsUnreliable {
		t.Fatal("reliability flags lost")
	}
	r.resetMaybeStack(0, 0, false)
	if relation.size() != 1 || r.relationCount != 9 || r.maybeKeysSet.Len() != 0 {
		t.Fatal("discarded assumptions became cached results")
	}
	flags := RelationComparisonResultFailed | RelationComparisonResultComplexityOverflow | RelationComparisonResultReportsUnmeasurable
	relation.set(ordinary, flags)
	relation.set(ordinary, flags)
	if relation.size() != 2 || relation.get(ordinary) != flags {
		t.Fatal("failure/overflow flags or replacement size changed")
	}
	// A new relater from this checker must see the same stable fallback IDs but
	// no recursive assumptions retained from its previous use.
	r.maybeKeysSet.Add(ordinary)
	c.putRelater(r)
	reused := c.getRelater()
	if reused.c != c || reused.maybeKeysSet.Len() != 0 || len(reused.maybeKeys) != 0 || c.internRelationHash(CacheHashKey{Hi: 42}) != fallback {
		t.Fatal("pooled relater lifetime changed key ownership")
	}
	c.putRelater(reused)
}
