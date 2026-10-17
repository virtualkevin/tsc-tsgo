package checker

import (
	"slices"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/jsnum"
)

func crossProductTestChecker(strict bool) *Checker {
	c := &Checker{strictNullChecks: strict, intersectionTypes: make(map[CacheHashKey]*Type)}
	c.neverType = c.newIntrinsicType(TypeFlagsNever, "never")
	c.unknownType = c.newIntrinsicType(TypeFlagsUnknown, "unknown")
	c.undefinedType = c.newIntrinsicType(TypeFlagsUndefined, "undefined")
	c.missingType = c.newIntrinsicType(TypeFlagsUndefined, "missing")
	c.nullType = c.newIntrinsicType(TypeFlagsNull, "null")
	return c
}

// The original mixed-radix traversal is an independent oracle for ordering and
// symbol/type identity, including combinations reduced by getIntersectionTypeEx.
func eagerCrossProductForTest(c *Checker, types []*Type, flags IntersectionFlags) []*Type {
	var result []*Type
	for i := range c.getCrossProductUnionSize(types) {
		parts := slices.Clone(types)
		n := i
		for j := len(types) - 1; j >= 0; j-- {
			if types[j].flags&TypeFlagsUnion != 0 {
				candidates := types[j].Types()
				parts[j] = candidates[n%len(candidates)]
				n /= len(candidates)
			}
		}
		if typ := c.getIntersectionTypeEx(parts, flags, nil); typ.flags&TypeFlagsNever == 0 {
			result = append(result, typ)
		}
	}
	return result
}

func TestCrossProductPruningMatchesEagerOrder(t *testing.T) {
	for _, strict := range []bool{false, true} {
		c := crossProductTestChecker(strict)
		a := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
		b := c.newLiteralType(TypeFlagsStringLiteral, "b", nil)
		freshA := c.getFreshTypeOfLiteralType(a)
		enumA := c.newLiteralType(TypeFlagsNumberLiteral|TypeFlagsEnumLiteral, jsnum.Number(1), nil)
		enumB := c.newLiteralType(TypeFlagsNumberLiteral|TypeFlagsEnumLiteral, jsnum.Number(1), nil)
		symbolA := c.newUniqueESSymbolType(&ast.Symbol{Name: "a"}, "a")
		symbolB := c.newUniqueESSymbolType(&ast.Symbol{Name: "b"}, "b")
		// Interfaces with no symbol are opaque to the empty-anonymous-object test.
		x := c.newObjectType(ObjectFlagsInterface, nil)
		y := c.newObjectType(ObjectFlagsInterface, nil)
		union := func(types ...*Type) *Type { return c.newUnionType(ObjectFlagsNone, types) }
		cases := [][]*Type{
			{union(a, b, x), union(b, a, y), union(a, x)},
			{union(freshA, b), union(a, b)},
			{union(enumA, enumB), union(c.getFreshTypeOfLiteralType(enumA), enumB)},
			{union(symbolA, symbolB), union(symbolB, symbolA)},
			{union(c.missingType, a), union(c.undefinedType, a)},
			{union(c.nullType, a), union(b, c.undefinedType)},
			{x, union(a, b), y},
		}
		for _, flags := range []IntersectionFlags{IntersectionFlagsNone, IntersectionFlagsNoSupertypeReduction, IntersectionFlagsNoConstraintReduction} {
			for i, types := range cases {
				want := eagerCrossProductForTest(c, types, flags)
				got := c.getCrossProductIntersections(types, flags)
				if !slices.Equal(got, want) {
					t.Fatalf("strict=%v flags=%v case=%d: output identities/order differ", strict, flags, i)
				}
			}
		}
	}
}

func TestCrossProductUnitNormalization(t *testing.T) {
	c := crossProductTestChecker(true)
	literal := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
	if c.getIntersectionUnitType(c.getFreshTypeOfLiteralType(literal)) != literal {
		t.Fatal("fresh literal was not regularized")
	}
	if c.getIntersectionUnitType(c.missingType) != c.undefinedType {
		t.Fatal("missing and undefined must be the same unit for pruning")
	}
	if c.getIntersectionUnitType(c.nullType) != c.nullType {
		t.Fatal("strict null must remain a unit")
	}
	c.strictNullChecks = false
	for _, typ := range []*Type{c.nullType, c.undefinedType, c.missingType} {
		if c.getIntersectionUnitType(typ) != nil {
			t.Fatal("non-strict nullable type incorrectly prunes a combination")
		}
	}
}

func TestCrossProductLateMemberResolutionGuard(t *testing.T) {
	c := crossProductTestChecker(true)
	symbol := &ast.Symbol{Flags: ast.SymbolFlagsTypeLiteral}
	literal := c.newObjectType(ObjectFlagsAnonymous, symbol)
	nested := c.newUnionType(ObjectFlagsNone, []*Type{c.newIntersectionType(ObjectFlagsNone, []*Type{literal})})
	if allIntersectionConstituentsWithoutMembersToResolve([]*Type{nested}) {
		t.Fatal("nested unresolved type literal must retain eager enumeration")
	}
	if literal.objectFlags&ObjectFlagsMembersResolved != 0 {
		t.Fatal("guard itself resolved members")
	}
	literal.objectFlags |= ObjectFlagsMembersResolved
	if !allIntersectionConstituentsWithoutMembersToResolve([]*Type{nested}) {
		t.Fatal("already resolved type literal should permit pruning")
	}
	literal.objectFlags &^= ObjectFlagsMembersResolved
	literal.symbol = nil
	if !allIntersectionConstituentsWithoutMembersToResolve([]*Type{nested}) {
		t.Fatal("symbol-less anonymous type should permit pruning")
	}
}

func TestCrossProductPruningDoesNotAlterInput(t *testing.T) {
	c := crossProductTestChecker(true)
	a := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
	b := c.newLiteralType(TypeFlagsStringLiteral, "b", nil)
	union := c.newUnionType(ObjectFlagsNone, []*Type{a, b})
	input := []*Type{union, union}
	before := slices.Clone(input)
	got := c.getCrossProductIntersections(input, IntersectionFlagsNone)
	if !slices.Equal(input, before) || !slices.Equal(union.Types(), []*Type{a, b}) {
		t.Fatal("enumeration mutated a source list")
	}
	if !slices.Equal(got, []*Type{a, b}) {
		t.Fatal("expected only matching unit intersections in original order")
	}
}
