package checker

import (
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
)

func TestUnionPropertyCacheMissDoesNotAllocateOrCacheAbsence(t *testing.T) {
	for _, skipAugment := range []bool{false, true} {
		c := lazyPropertyTestChecker()
		members := ast.SymbolTable{}
		object := c.newAnonymousType(nil, members, nil, nil, nil)
		union := c.newUnionType(ObjectFlagsNone, []*Type{object})
		for range 2 {
			if c.getUnionOrIntersectionProperty(union, "later", skipAugment) != nil {
				t.Fatal("missing property unexpectedly exists")
			}
		}
		data := union.AsUnionOrIntersectionType()
		if data.propertyCache != nil || data.propertyCacheWithoutFunctionPropertyAugment != nil {
			t.Fatal("failed property lookup allocated a cache")
		}
		later := lazyProperty(c, "later", c.stringType, false)
		members["later"] = later
		if c.getUnionOrIntersectionProperty(union, "later", skipAugment) != later {
			t.Fatal("previous miss hid a subsequently available member")
		}
	}
}

func TestUnionPropertyCacheSharesCompleteResultWithoutCopying(t *testing.T) {
	for _, isUnion := range []bool{false, true} {
		c := lazyPropertyTestChecker()
		property := lazyProperty(c, "value", c.stringType, false)
		left, right := lazyObject(c, property), lazyObject(c, property)
		var typ *Type
		if isUnion {
			typ = c.newUnionType(ObjectFlagsNone, []*Type{left, right})
		} else {
			typ = c.newIntersectionType(ObjectFlagsNone, []*Type{left, right})
		}
		if c.getUnionOrIntersectionProperty(typ, "value", true) != property {
			t.Fatal("non-augmented lookup lost constituent symbol identity")
		}
		data := typ.AsUnionOrIntersectionType()
		if data.propertyCache != nil || data.propertyCacheWithoutFunctionPropertyAugment["value"] != property {
			t.Fatal("non-augmented result was copied to the augmented cache")
		}
		// Resolution and discriminant computation can modify a cached symbol.
		// Reuse must keep the same pointer and observe those late updates.
		property.CheckFlags |= ast.CheckFlagsIsDiscriminantComputed | ast.CheckFlagsIsDiscriminant
		c.valueSymbolLinks.Get(property).resolvedType = c.numberType
		for range 2 {
			got := c.getUnionOrIntersectionProperty(typ, "value", false)
			if got != property || c.getTypeOfSymbol(got) != c.numberType || got.CheckFlags&ast.CheckFlagsIsDiscriminant == 0 {
				t.Fatal("augmented fallback lost identity or later symbol state")
			}
		}
		if data.propertyCache != nil {
			t.Fatal("augmented fallback allocated a duplicate cache")
		}
	}
}

func TestUnionPropertyCacheKeepsAugmentedPrecedence(t *testing.T) {
	c := lazyPropertyTestChecker()
	own := lazyProperty(c, "value", c.stringType, false)
	inherited := lazyProperty(c, "value", c.numberType, false)
	c.globalObjectType = lazyObject(c, inherited)
	typ := c.newIntersectionType(ObjectFlagsNone, []*Type{lazyObject(c, own), lazyObject(c)})
	augmented := c.getUnionOrIntersectionProperty(typ, "value", false)
	if augmented == nil || augmented == own {
		t.Fatal("fixture did not synthesize a distinct augmented result")
	}
	if c.getUnionOrIntersectionProperty(typ, "value", true) != own {
		t.Fatal("non-augmented lookup did not return the own property")
	}
	if c.getUnionOrIntersectionProperty(typ, "value", false) != augmented {
		t.Fatal("later non-augmented result replaced an existing augmented symbol")
	}
}

func TestUnionPropertyCacheDoesNotReusePartialResults(t *testing.T) {
	for _, partial := range []ast.CheckFlags{ast.CheckFlagsReadPartial, ast.CheckFlagsWritePartial} {
		c := lazyPropertyTestChecker()
		own := lazyProperty(c, "value", c.stringType, false)
		var other *Type
		if partial == ast.CheckFlagsReadPartial {
			other = lazyObject(c)
			// The augment fills the missing member with the same original
			// symbol, so its complete result must be that original symbol.
			c.globalObjectType = lazyObject(c, own)
		} else {
			other = c.newAnonymousType(nil, ast.SymbolTable{}, nil, nil,
				[]*IndexInfo{c.newIndexInfo(c.stringType, c.stringType, false, nil, nil)})
		}
		typ := c.newUnionType(ObjectFlagsNone, []*Type{lazyObject(c, own), other})
		without := c.getUnionOrIntersectionProperty(typ, "value", true)
		if without == nil || without.CheckFlags&partial == 0 {
			t.Fatalf("fixture did not create partial flag %v", partial)
		}
		with := c.getUnionOrIntersectionProperty(typ, "value", false)
		if with == nil || with == without {
			t.Fatal("augmented request reused a partial non-augmented result")
		}
		if partial == ast.CheckFlagsReadPartial && (with != own || with.CheckFlags&ast.CheckFlagsPartial != 0) {
			t.Fatal("Object augment did not restore the complete original symbol")
		}
		if c.getUnionOrIntersectionProperty(typ, "value", true) != without || c.getUnionOrIntersectionProperty(typ, "value", false) != with {
			t.Fatal("the two cache modes did not preserve their distinct identities")
		}
		if partial == ast.CheckFlagsReadPartial && c.getPropertyOfUnionOrIntersectionType(typ, "value", true) != nil {
			t.Fatal("public property lookup stopped filtering read-partial symbols")
		}
	}
}

func TestUnionPropertyCachePreservesReentrantPopulation(t *testing.T) {
	for _, skipAugment := range []bool{false, true} {
		c := lazyPropertyTestChecker()
		parameter := c.newTypeParameter(nil)
		original := lazyProperty(c, "outer", parameter, false)
		nested := lazyProperty(c, "nested", c.stringType, false)
		var typ *Type
		calls := 0
		mapper := newFunctionTypeMapper(func(input *Type) *Type {
			if input != parameter {
				return input
			}
			calls++
			if c.getUnionOrIntersectionProperty(typ, "nested", skipAugment) != nested {
				t.Fatal("reentrant lookup returned the wrong nested symbol")
			}
			return c.stringType
		})
		instantiated := c.newInstantiatedSymbol(original, mapper)
		left := lazyObject(c, instantiated, nested)
		right := lazyObject(c, lazyProperty(c, "outer", c.stringType, false), nested)
		typ = c.newIntersectionType(ObjectFlagsNone, []*Type{left, right})
		outer := c.getUnionOrIntersectionProperty(typ, "outer", skipAugment)
		if outer == nil || calls != 1 {
			t.Fatalf("outer result %p triggered %d mapper calls, want a result and 1", outer, calls)
		}
		data := typ.AsUnionOrIntersectionType()
		cache := data.propertyCache
		if skipAugment {
			cache = data.propertyCacheWithoutFunctionPropertyAugment
		}
		if len(cache) != 2 || cache["nested"] != nested || cache["outer"] != outer {
			t.Fatal("outer synthesis replaced the map populated by its recursive worker")
		}
		if c.getUnionOrIntersectionProperty(typ, "outer", skipAugment) != outer || calls != 1 {
			t.Fatal("repeated lookup changed symbol identity or repeated instantiation")
		}
	}
}

func TestUnionPropertyCachePreservesRecursiveAugmentedWinner(t *testing.T) {
	for _, outerPartial := range []bool{false, true} {
		for _, innerPartial := range []bool{false, true} {
			for _, existingAugmented := range []bool{false, true} {
				c := lazyPropertyTestChecker()
				parameter := c.newTypeParameter(nil)
				original := lazyProperty(c, "value", parameter, false)
				rightProp := lazyProperty(c, "value", c.stringType, false)
				rightMembers := ast.SymbolTable{}
				if !outerPartial {
					rightMembers["value"] = rightProp
				}
				var typ *Type
				var instantiated, inner *ast.Symbol
				mapper := newFunctionTypeMapper(func(input *Type) *Type {
					if input != parameter {
						return input
					}
					// Model nested work after this member's type becomes known,
					// while the containing union's outer synthesis is still running.
					c.valueSymbolLinks.Get(instantiated).resolvedType = c.stringType
					if innerPartial {
						delete(rightMembers, "value")
					} else {
						rightMembers["value"] = rightProp
					}
					inner = c.getUnionOrIntersectionProperty(typ, "value", true)
					if outerPartial {
						delete(rightMembers, "value")
					} else {
						rightMembers["value"] = rightProp
					}
					return c.stringType
				})
				instantiated = c.newInstantiatedSymbol(original, mapper)
				typ = c.newUnionType(ObjectFlagsNone, []*Type{
					lazyObject(c, instantiated),
					c.newAnonymousType(nil, rightMembers, nil, nil, nil),
				})
				data := typ.AsUnionOrIntersectionType()
				var existing *ast.Symbol
				if existingAugmented {
					existing = lazyProperty(c, "value", c.numberType, false)
					data.propertyCache = ast.SymbolTable{"value": existing}
				}
				outer := c.getUnionOrIntersectionProperty(typ, "value", true)
				if outer == nil || inner == nil || outer == inner {
					t.Fatal("fixture did not synthesize distinct recursive results")
				}
				if (outer.CheckFlags&ast.CheckFlagsReadPartial != 0) != outerPartial || (inner.CheckFlags&ast.CheckFlagsReadPartial != 0) != innerPartial {
					t.Fatal("fixture did not preserve the requested partial states")
				}
				if data.propertyCacheWithoutFunctionPropertyAugment["value"] != outer {
					t.Fatal("outer result did not replace the non-augmented entry")
				}
				var winner *ast.Symbol
				switch {
				case existingAugmented:
					winner = existing
				case !innerPartial:
					winner = inner
				case !outerPartial:
					winner = outer
				}
				if winner != nil {
					if c.getUnionOrIntersectionProperty(typ, "value", false) != winner {
						t.Fatalf("wrong augmented winner for outerPartial=%v innerPartial=%v existing=%v", outerPartial, innerPartial, existingAugmented)
					}
				} else if data.propertyCache != nil {
					t.Fatal("partial-only recursive results allocated an augmented cache")
				}
			}
		}
	}
}

func TestUnionPropertyCacheSameSymbolRecursiveOverwriteNeedsNoCopy(t *testing.T) {
	c := lazyPropertyTestChecker()
	property := lazyProperty(c, "value", c.stringType, false)
	object := lazyObject(c, property)
	bigint := c.newIntrinsicType(TypeFlagsBigInt, "bigint")
	typ := c.newIntersectionType(ObjectFlagsNone, []*Type{bigint})
	calls := 0
	c.getGlobalBigIntType = func() *Type {
		calls++
		// The lazy global resolver can initiate another lookup after its
		// own result is available, before the outer property lookup returns.
		c.getGlobalBigIntType = func() *Type { return object }
		if c.getUnionOrIntersectionProperty(typ, "value", true) != property {
			t.Fatal("nested global-type lookup changed property identity")
		}
		return object
	}
	if c.getUnionOrIntersectionProperty(typ, "value", true) != property || calls != 1 {
		t.Fatal("outer lookup did not reuse the same resolved property")
	}
	if c.getUnionOrIntersectionProperty(typ, "value", false) != property || typ.AsUnionOrIntersectionType().propertyCache != nil {
		t.Fatal("same-symbol recursive overwrite allocated a duplicate augmented entry")
	}
}
