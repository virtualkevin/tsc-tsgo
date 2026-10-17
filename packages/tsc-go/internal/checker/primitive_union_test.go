package checker

import (
	"fmt"
	"slices"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/jsnum"
)

// Compare the entry-point shortcut against the full relation engine, across all
// relation kinds and freshness forms. The engine remains the semantic oracle;
// these cases also exercise the intentional large-union fallback.
func TestPrimitiveUnionRelationsMatchFullRelater(t *testing.T) {
	c := &Checker{strictNullChecks: true}
	c.assignableRelation = &Relation{}
	c.comparableRelation = &Relation{}
	c.subtypeRelation = &Relation{}
	c.strictSubtypeRelation = &Relation{}
	c.identityRelation = &Relation{}
	c.stringType = c.newIntrinsicType(TypeFlagsString, "string")
	c.numberType = c.newIntrinsicType(TypeFlagsNumber, "number")
	c.bigintType = c.newIntrinsicType(TypeFlagsBigInt, "bigint")
	c.esSymbolType = c.newIntrinsicType(TypeFlagsESSymbol, "symbol")
	c.neverType = c.newIntrinsicType(TypeFlagsNever, "never")
	c.anyType = c.newIntrinsicType(TypeFlagsAny, "any")
	c.unknownType = c.newIntrinsicType(TypeFlagsUnknown, "unknown")
	c.regularFalseType = c.newLiteralType(TypeFlagsBooleanLiteral, false, nil)
	c.regularTrueType = c.newLiteralType(TypeFlagsBooleanLiteral, true, nil)
	a := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
	b := c.newLiteralType(TypeFlagsStringLiteral, "b", nil)
	d := c.newLiteralType(TypeFlagsStringLiteral, "d", nil)
	e := c.newLiteralType(TypeFlagsStringLiteral, "e", nil)
	n := c.newLiteralType(TypeFlagsNumberLiteral, jsnum.Number(1), nil)
	big := c.newLiteralType(TypeFlagsBigIntLiteral, jsnum.NewPseudoBigInt("1", false), nil)
	enum := c.newLiteralType(TypeFlagsNumberLiteral|TypeFlagsEnumLiteral, jsnum.Number(1), nil)
	enum.symbol = &ast.Symbol{Name: "Member", Flags: ast.SymbolFlagsEnumMember, Parent: &ast.Symbol{Name: "E", Flags: ast.SymbolFlagsRegularEnum}}
	otherEnum := c.newLiteralType(TypeFlagsNumberLiteral|TypeFlagsEnumLiteral, jsnum.Number(1), nil)
	otherEnum.symbol = &ast.Symbol{Name: "Member", Flags: ast.SymbolFlagsEnumMember, Parent: &ast.Symbol{Name: "Other", Flags: ast.SymbolFlagsRegularEnum}}
	union := func(types ...*Type) *Type {
		slices.SortFunc(types, CompareTypes)
		return c.newUnionType(ObjectFlagsPrimitiveUnion, types)
	}
	targets := []*Type{
		union(c.stringType, c.numberType),
		union(a, b),
		union(c.getFreshTypeOfLiteralType(a), c.getFreshTypeOfLiteralType(b)),
		union(c.regularFalseType, c.regularTrueType),
		union(enum, b),
		union(a, b, d, e),
		union(c.numberType, c.bigintType, c.esSymbolType, c.regularFalseType),
	}
	sources := []*Type{c.stringType, c.numberType, c.bigintType, c.esSymbolType, c.neverType, c.anyType, c.unknownType, a, b, n, big, enum, otherEnum, c.regularFalseType, c.regularTrueType}
	for _, literal := range []*Type{a, b, n, big, enum, otherEnum, c.regularFalseType, c.regularTrueType} {
		sources = append(sources, c.getFreshTypeOfLiteralType(literal))
	}
	relations := []struct {
		name string
		r    *Relation
	}{
		{"assignable", c.assignableRelation},
		{"comparable", c.comparableRelation},
		{"subtype", c.subtypeRelation},
		{"strict subtype", c.strictSubtypeRelation},
		{"identity", c.identityRelation},
	}
	for _, relation := range relations {
		for i, source := range sources {
			for j, target := range targets {
				t.Run(fmt.Sprintf("%s/source%d/target%d", relation.name, i, j), func(t *testing.T) {
					got := c.isTypeRelatedTo(source, target, relation.r)
					want := c.checkTypeRelatedTo(source, target, relation.r, nil)
					if got != want {
						t.Fatalf("shortcut = %v; full relation = %v", got, want)
					}
				})
			}
		}
	}
	// Explicit semantic expectations are independent of the extracted helper used
	// by both paths above. Columns follow the five relation kinds in relations.
	for _, test := range []struct {
		name           string
		source, target *Type
		want           [5]bool
	}{
		{"literal to base primitive", a, targets[0], [5]bool{true, true, true, true, false}},
		{"literal membership", a, targets[1], [5]bool{true, true, true, true, false}},
		{"fresh source membership", c.getFreshTypeOfLiteralType(a), targets[1], [5]bool{true, true, true, true, false}},
		{"fresh target membership", a, targets[2], [5]bool{true, true, true, true, false}},
		{"missing literal", e, targets[1], [5]bool{}},
		{"boolean membership", c.regularTrueType, targets[3], [5]bool{true, true, true, true, false}},
		{"missing boolean", c.regularTrueType, targets[6], [5]bool{}},
		{"bigint to base primitive", big, targets[6], [5]bool{true, true, true, true, false}},
		{"missing bigint", big, targets[0], [5]bool{}},
		{"enum member identity", enum, targets[4], [5]bool{true, true, true, true, false}},
		{"distinct enum parents", otherEnum, targets[4], [5]bool{}},
	} {
		for i, relation := range relations {
			t.Run(test.name+"/"+relation.name, func(t *testing.T) {
				if got := c.isTypeRelatedTo(test.source, test.target, relation.r); got != test.want[i] {
					t.Fatalf("relation = %v, want %v", got, test.want[i])
				}
			})
		}
	}
	// Numeric literals are assignable/comparable to matching enum values, but
	// are not subtypes. String primitives compare to string literals in reverse.
	enumUnion := targets[4]
	if !c.isTypeRelatedTo(n, enumUnion, c.assignableRelation) || !c.isTypeRelatedTo(n, enumUnion, c.comparableRelation) || c.isTypeRelatedTo(n, enumUnion, c.subtypeRelation) || c.isTypeRelatedTo(n, enumUnion, c.strictSubtypeRelation) {
		t.Fatal("numeric enum assignment/subtype distinction was lost")
	}
	if !c.isTypeRelatedTo(c.stringType, targets[1], c.comparableRelation) || c.isTypeRelatedTo(c.stringType, targets[1], c.assignableRelation) {
		t.Fatal("comparability must also check the reverse direction")
	}
	// A four-member primitive union with a non-member source must still use
	// the full relater and populate its cache. Calling again must reuse it.
	c.assignableRelation.results = nil
	if c.isTypeRelatedTo(c.numberType, targets[5], c.assignableRelation) {
		t.Fatal("number must not be assignable to four string literals")
	}
	size := c.assignableRelation.size()
	if size == 0 {
		t.Fatal("large undecided union bypassed the relation cache")
	}
	c.isTypeRelatedTo(c.numberType, targets[5], c.assignableRelation)
	if c.assignableRelation.size() != size {
		t.Fatal("repeated large-union relation did not reuse its cache")
	}
}
