package checker

import (
	"slices"

	"github.com/microsoft/typescript-go/internal/ast"
)

// Enumerate in the original Cartesian order, but skip a prefix containing two
// distinct unit types: every extension reduces to never before creating or
// caching a type. The caller first ensures that skipped combinations cannot
// resolve late-bound members as a side effect.
func (c *Checker) addCrossProductIntersections(types []*Type, flags IntersectionFlags, constituents []*Type, index int, unit *Type, intersections []*Type) []*Type {
	if index == len(types) {
		t := c.getIntersectionTypeEx(slices.Clone(constituents), flags, nil)
		if t.flags&TypeFlagsNever == 0 {
			intersections = append(intersections, t)
		}
		return intersections
	}
	t := types[index]
	candidates := types[index : index+1]
	if t.flags&TypeFlagsUnion != 0 {
		candidates = t.Types()
	}
	for _, candidate := range candidates {
		candidateUnit := c.getIntersectionUnitType(candidate)
		if candidateUnit != nil && unit != nil && candidateUnit != unit {
			continue
		}
		constituents[index] = candidate
		nextUnit := unit
		if nextUnit == nil {
			nextUnit = candidateUnit
		}
		intersections = c.addCrossProductIntersections(types, flags, constituents, index+1, nextUnit, intersections)
	}
	return intersections
}

// Match addTypeToIntersection's normalization, including fresh literals,
// missing optional properties and nullable types without strictNullChecks.
func (c *Checker) getIntersectionUnitType(t *Type) *Type {
	if t.flags&TypeFlagsUnit == 0 || !c.strictNullChecks && t.flags&TypeFlagsNullable != 0 {
		return nil
	}
	regular := c.getRegularTypeOfLiteralType(t)
	if regular == c.missingType {
		return c.undefinedType
	}
	return regular
}

// IsEmptyAnonymousObjectType can bind a type literal's late-bound members.
// Preserve the eager traversal whenever any constituent could do that.
func allIntersectionConstituentsWithoutMembersToResolve(types []*Type) bool {
	for _, t := range types {
		if t.flags&TypeFlagsUnionOrIntersection != 0 {
			if !allIntersectionConstituentsWithoutMembersToResolve(t.Types()) {
				return false
			}
		} else if t.flags&TypeFlagsObject != 0 && t.objectFlags&ObjectFlagsAnonymous != 0 &&
			t.objectFlags&ObjectFlagsMembersResolved == 0 && t.symbol != nil && t.symbol.Flags&ast.SymbolFlagsTypeLiteral != 0 {
			return false
		}
	}
	return true
}
