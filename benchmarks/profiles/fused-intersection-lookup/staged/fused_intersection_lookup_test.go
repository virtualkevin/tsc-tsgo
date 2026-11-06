package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func fusedFixture() (*Checker, *Type, *ast.Symbol) {
	c := lazyPropertyTestChecker()
	p := lazyProperty(c, "value", c.stringType, false)
	typ := c.newIntersectionType(ObjectFlagsIsNeverIntersectionComputed, []*Type{lazyObject(c, p), lazyObject(c, p)})
	d := typ.AsIntersectionType()
	d.resolvedApparentType = typ
	d.propertyCacheWithoutFunctionPropertyAugment = ast.SymbolTable{"value": p}
	return c, typ, p
}

func TestFusedIntersectionGuards(t *testing.T) {
	c, typ, p := fusedFixture()
	if cachedIntersectionProperty(typ, "value") != p {
		t.Fatal("eligible lookup missed")
	}
	if cachedIntersectionProperty(typ, "missing") != nil {
		t.Fatal("absence cached as present")
	}
	flags := typ.objectFlags
	for _, bad := range []ObjectFlags{0, flags | ObjectFlagsMapped, flags | ObjectFlagsIsNeverIntersection} {
		typ.objectFlags = bad
		if cachedIntersectionProperty(typ, "value") != nil {
			t.Fatal("unsafe flags admitted", bad)
		}
	}
	typ.objectFlags = flags
	d := typ.AsIntersectionType()
	for _, other := range []*Type{nil, c.stringType} {
		d.resolvedApparentType = other
		if cachedIntersectionProperty(typ, "value") != nil {
			t.Fatal("nonidentity apparent type admitted")
		}
	}
	d.resolvedApparentType = typ
	p.CheckFlags |= ast.CheckFlagsReadPartial
	if cachedIntersectionProperty(typ, "value") != nil {
		t.Fatal("read-partial admitted")
	}
	p.CheckFlags = ast.CheckFlagsWritePartial
	if cachedIntersectionProperty(typ, "value") != p {
		t.Fatal("write-partial must preserve original read behavior")
	}
	typ.flags = TypeFlagsUnion
	if cachedIntersectionProperty(typ, "value") != nil {
		t.Fatal("nonintersection admitted")
	}
}

func TestFusedIntersectionCurrentCacheAndSymbolState(t *testing.T) {
	c, typ, p := fusedFixture()
	d := typ.AsIntersectionType()
	original := func() *Type {
		prop := c.getPropertyOfType(typ, "value")
		if prop != nil {
			return c.getTypeOfSymbol(prop)
		}
		return nil
	}
	check := func(want *Type) {
		t.Helper()
		before := [3]uint32{c.TotalInstantiationCount, c.TypeCount, c.SymbolCount}
		if got := c.getTypeOfPropertyOfType(typ, "value"); got != want || got != original() {
			t.Fatal("query differed", got, want)
		}
		if after := [3]uint32{c.TotalInstantiationCount, c.TypeCount, c.SymbolCount}; after != before {
			t.Fatal("completed lookup added work", before, after)
		}
	}
	check(c.stringType)
	c.valueSymbolLinks.Get(p).resolvedType = c.numberType
	check(c.numberType)
	replacement := lazyProperty(c, "value", c.undefinedType, false)
	// Both entries may legitimately differ. Non-augmented lookup has priority.
	d.propertyCache = ast.SymbolTable{"value": p}
	d.propertyCacheWithoutFunctionPropertyAugment = ast.SymbolTable{"value": replacement}
	check(c.undefinedType)
	d.propertyCacheWithoutFunctionPropertyAugment = nil
	if cachedIntersectionProperty(typ, "value") != nil {
		t.Fatal("old map retained")
	}
	// Re-materialize through the original constituents. The original augmented winner stays.
	check(c.numberType)
	if d.propertyCache["value"] != p {
		t.Fatal("augmented winner changed")
	}
}

func TestFusedIntersectionFallbackHistories(t *testing.T) {
	c, typ, p := fusedFixture()
	d := typ.AsIntersectionType()
	// Apparent conversion must be followed rather than reading the original cache.
	d.resolvedApparentType = lazyObject(c, lazyProperty(c, "value", c.numberType, false))
	if c.getTypeOfPropertyOfType(typ, "value") != c.numberType {
		t.Fatal("apparent conversion bypassed")
	}
	d.resolvedApparentType = typ
	typ.objectFlags |= ObjectFlagsIsNeverIntersection
	if c.getTypeOfPropertyOfType(typ, "value") != nil {
		t.Fatal("never reduction bypassed")
	}
	typ.objectFlags &^= ObjectFlagsIsNeverIntersection
	p.CheckFlags |= ast.CheckFlagsReadPartial
	replacement := lazyProperty(c, "value", c.numberType, false)
	d.propertyCache = ast.SymbolTable{"value": replacement}
	if c.getTypeOfPropertyOfType(typ, "value") != c.numberType {
		t.Fatal("partial fallback bypassed")
	}
	p.CheckFlags &^= ast.CheckFlagsReadPartial
	if c.getTypeOfPropertyOfType(typ, "value") != c.stringType {
		t.Fatal("later complete symbol not observed")
	}
}

func TestFusedIntersectionInstantiatedSymbolQuery(t *testing.T) {
	c, typ, p := fusedFixture()
	// The fast path must still execute getTypeOfSymbol, not return a previously seen type.
	target := lazyProperty(c, "target", c.numberType, false)
	links := c.valueSymbolLinks.Get(p)
	links.resolvedType = nil
	links.target = target
	p.CheckFlags |= ast.CheckFlagsInstantiated
	if c.getTypeOfPropertyOfType(typ, "value") != c.numberType || links.resolvedType != c.numberType {
		t.Fatal("lazy symbol resolution skipped")
	}
	links.resolvedType = nil
	c.valueSymbolLinks.Get(target).resolvedType = c.stringType
	if c.getTypeOfPropertyOfType(typ, "value") != c.stringType {
		t.Fatal("new symbol state hidden")
	}
}
