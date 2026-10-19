package checker

import (
	"fmt"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
)

func lazyPropertyTestChecker() *Checker {
	c := pendingTestChecker()
	c.strictNullChecks = true
	c.stringLiteralTypes = make(map[string]*Type)
	c.assignableRelation = &Relation{}
	c.identityRelation = &Relation{}
	c.comparableRelation = &Relation{}
	c.subtypeRelation = &Relation{}
	c.strictSubtypeRelation = &Relation{}
	c.unionTypes = make(map[CacheHashKey]*Type)
	c.intersectionTypes = make(map[CacheHashKey]*Type)
	c.neverType = c.newIntrinsicType(TypeFlagsNever, "never")
	c.anyType = c.newIntrinsicType(TypeFlagsAny, "any")
	c.errorType = c.newIntrinsicType(TypeFlagsAny, "error")
	c.unknownType = c.newIntrinsicType(TypeFlagsUnknown, "unknown")
	c.stringType = c.newIntrinsicType(TypeFlagsString, "string")
	c.numberType = c.newIntrinsicType(TypeFlagsNumber, "number")
	c.undefinedType = c.newIntrinsicType(TypeFlagsUndefined, "undefined")
	c.missingType = c.newIntrinsicType(TypeFlagsUndefined, "missing")
	c.globalObjectType = c.newAnonymousType(nil, ast.SymbolTable{}, nil, nil, nil)
	return c
}

func lazyProperty(c *Checker, name string, typ *Type, optional bool) *ast.Symbol {
	flags := ast.SymbolFlagsProperty
	if optional {
		flags |= ast.SymbolFlagsOptional
	}
	prop := c.newSymbol(flags, name)
	c.valueSymbolLinks.Get(prop).resolvedType = typ
	return prop
}

func lazyObject(c *Checker, props ...*ast.Symbol) *Type {
	members := make(ast.SymbolTable)
	for _, prop := range props {
		members[prop.Name] = prop
	}
	return c.newAnonymousType(nil, members, nil, nil, nil)
}

func TestLazyIntersectionReductionMatchesEagerProperties(t *testing.T) {
	c := lazyPropertyTestChecker()
	a := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
	b := c.newLiteralType(TypeFlagsStringLiteral, "b", nil)
	types := []*Type{a, b, c.stringType, c.numberType, c.anyType, c.neverType}
	for _, optional := range []bool{false, true} {
		for i, left := range types {
			for j, right := range types {
				t.Run(fmt.Sprintf("optional=%v/%d/%d", optional, i, j), func(t *testing.T) {
					first := lazyObject(c, lazyProperty(c, "tag", left, optional), lazyProperty(c, "left", c.numberType, false))
					second := lazyObject(c, lazyProperty(c, "tag", right, optional), lazyProperty(c, "right", c.numberType, false))
					intersection := c.newIntersectionType(ObjectFlagsNone, []*Type{first, second})
					got := c.hasNeverReducedProperty(intersection)
					want := false
					for _, prop := range c.getPropertiesOfUnionOrIntersectionType(intersection) {
						if c.isNeverReducedProperty(prop) {
							want = true
							break
						}
					}
					if got != want {
						t.Fatalf("lazy=%v, original eager property scan=%v", got, want)
					}
					if !optional && i == 0 && j == 1 && !got {
						t.Fatal("distinct required literal tags must reduce to never")
					}
					if optional && got {
						t.Fatal("optional tag conflicts cannot reduce the entire intersection")
					}
					if c.hasNeverReducedProperty(intersection) != want {
						t.Fatal("resolved-property fallback changed the answer")
					}
				})
			}
		}
	}
}

func TestLazyUnmatchedPropertyMatchesEagerScan(t *testing.T) {
	c := lazyPropertyTestChecker()
	a := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
	b := c.newLiteralType(TypeFlagsStringLiteral, "b", nil)
	objects := []*Type{
		lazyObject(c),
		lazyObject(c, lazyProperty(c, "tag", a, false)),
		lazyObject(c, lazyProperty(c, "tag", b, false)),
		lazyObject(c, lazyProperty(c, "tag", c.stringType, true)),
		lazyObject(c, lazyProperty(c, "tag", c.anyType, false), lazyProperty(c, "extra", c.numberType, true)),
		lazyObject(c, lazyProperty(c, "extra", c.numberType, false)),
	}
	for _, union := range []bool{false, true} {
		for i, first := range objects {
			for j, second := range objects {
				for k, source := range objects {
					for _, discriminants := range []bool{false, true} {
						var target *Type
						if union {
							target = c.newUnionType(ObjectFlagsNone, []*Type{first, second})
						} else {
							target = c.newIntersectionType(ObjectFlagsNone, []*Type{first, second})
						}
						got := c.hasUnmatchedProperty(source, target, discriminants)
						want := c.getUnmatchedProperty(source, target, false, discriminants) != nil
						if got != want {
							t.Fatalf("union=%v parts=%d,%d source=%d discriminants=%v: lazy=%v eager=%v", union, i, j, k, discriminants, got, want)
						}
					}
				}
			}
		}
	}
}

func TestLazyUnmatchedPropertyDoesNotSynthesizeBroadUnion(t *testing.T) {
	c := lazyPropertyTestChecker()
	var left, right []*ast.Symbol
	for i := range 96 {
		name := fmt.Sprintf("p%02d", i)
		left = append(left, lazyProperty(c, name, c.stringType, false))
		right = append(right, lazyProperty(c, name, c.numberType, false))
	}
	first, second := lazyObject(c, left...), lazyObject(c, right...)
	union := c.newUnionType(ObjectFlagsNone, []*Type{first, second})
	before := c.SymbolCount
	if c.hasUnmatchedProperty(first, union, true) {
		t.Fatal("all required names exist and none is a discriminant")
	}
	if c.SymbolCount != before || union.AsUnionType().resolvedProperties != nil {
		t.Fatal("boolean unrelatedness predicate synthesized the broad union's properties")
	}
}

func TestLazyUnmatchedPropertyContinuesPastIndexedUnionConstituent(t *testing.T) {
	c := lazyPropertyTestChecker()
	indexed := c.newAnonymousType(nil, ast.SymbolTable{}, nil, nil,
		[]*IndexInfo{c.newIndexInfo(c.stringType, c.stringType, false, nil, nil)})
	required := lazyObject(c, lazyProperty(c, "required", c.stringType, false))
	empty := lazyObject(c)
	union := c.newUnionType(ObjectFlagsNone, []*Type{indexed, required})
	if c.hasUnmatchedProperty(empty, union, false) {
		t.Fatal("index-signature union property is partial, not required")
	}
	property := union.AsUnionType().propertyCachePairs["required"].augmented
	if property == nil || property.CheckFlags&ast.CheckFlagsWritePartial == 0 {
		t.Fatal("search did not continue past the first indexed constituent to its partial property")
	}
	if c.getUnmatchedProperty(empty, union, false, false) != nil {
		t.Fatal("original eager scan disagrees")
	}
	if !c.isUnmatchedProperty(empty, property, true, false) {
		t.Fatal("explicit optional/partial requirement was lost")
	}
	intersection := c.newIntersectionType(ObjectFlagsNone, []*Type{indexed, required})
	if !c.hasUnmatchedProperty(empty, intersection, false) {
		t.Fatal("intersection's explicit property is required despite the other index signature")
	}
	if c.getUnmatchedProperty(empty, intersection, false, false) == nil {
		t.Fatal("original eager intersection scan disagrees")
	}
}
