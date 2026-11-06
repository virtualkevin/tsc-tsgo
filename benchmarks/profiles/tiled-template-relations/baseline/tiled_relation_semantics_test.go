package checker

import "testing"

func tiledSemanticPair(c *Checker) (*Type, *Type) {
	return c.newTemplateLiteralType([]string{"left-", ""}, []*Type{c.stringType}), c.newTemplateLiteralType([]string{"right-", ""}, []*Type{c.stringType})
}
func TestTiledRelationReplay(t *testing.T) {
	c := lazyPropertyTestChecker()
	source, target := tiledSemanticPair(c)
	r := c.getRelater()
	r.relation = c.assignableRelation
	r.relationCount = 100
	if r.recursiveTypeRelatedTo(source, target, false, IntersectionStateNone, RecursionFlagsBoth) != TernaryFalse {
		t.Fatal("expected failure")
	}
	if r.relation.size() != 1 || r.relationCount != 99 {
		t.Fatal("first budget", r.relation.size(), r.relationCount)
	}
	if r.recursiveTypeRelatedTo(source, target, false, IntersectionStateNone, RecursionFlagsBoth) != TernaryFalse || r.relationCount != 99 {
		t.Fatal("cached budget")
	}
	key, _ := getRelationKey(source, target, IntersectionStateNone, false, false)
	r.relation.set(key, RelationComparisonResultFailed|RelationComparisonResultReportsUnreliable)
	c.reliabilityFlags = 0
	if r.recursiveTypeRelatedTo(source, target, false, IntersectionStateNone, RecursionFlagsBoth) != TernaryFalse || c.reliabilityFlags&RelationComparisonResultReportsUnreliable == 0 {
		t.Fatal("reliability replay")
	}
	r.relation.set(key, RelationComparisonResultFailed|RelationComparisonResultStackDepthOverflow)
	if r.relation.get(key) != (RelationComparisonResultFailed|RelationComparisonResultStackDepthOverflow) || r.relation.size() != 1 {
		t.Fatal("overflow bits")
	}
	*r.relation = Relation{}
	if r.relation.size() != 0 || r.relation.get(key) != 0 {
		t.Fatal("reset")
	}
	c.putRelater(r)
}
func TestTiledRelationMaybeStack(t *testing.T) {
	c := lazyPropertyTestChecker()
	a, b := tiledSemanticPair(c)
	packed, _ := getRelationKey(a, b, IntersectionStateNone, false, false)
	hashed, _ := getRelationKey(c.stringType, c.numberType, IntersectionStateNone, false, false)
	r := c.getRelater()
	r.relation = c.assignableRelation
	r.relationCount = 100
	for _, key := range []CacheHashKey{packed, hashed} {
		r.maybeKeys = append(r.maybeKeys, key)
		r.maybeKeysSet.Add(key)
	}
	r.resetMaybeStack(0, RelationComparisonResultReportsUnmeasurable, true)
	want := RelationComparisonResultSucceeded | RelationComparisonResultReportsUnmeasurable
	if r.relation.get(packed) != want || r.relation.get(hashed) != want || r.relationCount != 98 || r.relation.size() != 2 || len(r.maybeKeys) != 0 || r.maybeKeysSet.Has(packed) || r.maybeKeysSet.Has(hashed) {
		t.Fatal("success propagation")
	}
	c.putRelater(r)
}
