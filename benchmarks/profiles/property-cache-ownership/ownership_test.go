package checker

import "testing"

// A populated type cache is consulted before any receiver-local synthesis.
func TestPropertyCacheOwnershipAcrossReceivers(t *testing.T) {
	owner := lazyPropertyTestChecker()
	other := lazyPropertyTestChecker()
	original := lazyProperty(owner, "value", owner.stringType, false)
	replacement := lazyProperty(owner, "value", owner.numberType, false)
	object := lazyObject(owner, original)
	typ := owner.newUnionType(ObjectFlagsNone, []*Type{object})
	for _, skip := range []bool{true, false} {
		if owner.getUnionOrIntersectionProperty(typ, "value", skip) != original {
			t.Fatal("owner lookup identity")
		}
	}
	object.AsStructuredType().members["value"] = replacement
	for _, receiver := range []*Checker{other, owner, other} {
		for _, skip := range []bool{false, true} {
			if receiver.getUnionOrIntersectionProperty(typ, "value", skip) != original {
				t.Fatal("receiver change discarded published type-owned cache")
			}
		}
	}
}

func TestPropertyCacheOwnershipDistinctTypes(t *testing.T) {
	c := lazyPropertyTestChecker()
	original := lazyProperty(c, "value", c.stringType, false)
	replacement := lazyProperty(c, "value", c.numberType, false)
	object := lazyObject(c, original)
	first := c.newUnionType(ObjectFlagsNone, []*Type{object})
	second := c.newUnionType(ObjectFlagsNone, []*Type{object})
	if first == second {
		t.Fatal("fixture must create distinct type identities")
	}
	if c.getUnionOrIntersectionProperty(first, "value", true) != original {
		t.Fatal("first lookup")
	}
	object.AsStructuredType().members["value"] = replacement
	if c.getUnionOrIntersectionProperty(second, "value", true) != replacement {
		t.Fatal("distinct type inherited another type's cache")
	}
	if c.getUnionOrIntersectionProperty(first, "value", true) != original {
		t.Fatal("published cache replaced")
	}
}
