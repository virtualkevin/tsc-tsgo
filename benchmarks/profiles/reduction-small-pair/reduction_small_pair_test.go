package checker

import (
	"fmt"
	"github.com/microsoft/typescript-go/internal/ast"
	"slices"
	"testing"
)

// Frozen pre-candidate grouping algorithm, for boundary/fallback comparison.
func (c *Checker) hasNeverReducedPropertyReference(t *Type) bool {
	if resolved := t.AsIntersectionType().resolvedProperties; resolved != nil {
		for _, prop := range resolved {
			if c.isNeverReducedProperty(prop) {
				return true
			}
		}
		return false
	}
	skipped := c.getCostliestConstituent(t)
	byName := make(map[string][]*ast.Symbol)
	var names []string
	for _, current := range t.Types() {
		if current == skipped {
			continue
		}
		for _, prop := range c.getPropertiesOfType(current) {
			props, seen := byName[prop.Name]
			if !seen {
				names = append(names, prop.Name)
			}
			if !slices.Contains(props, prop) {
				byName[prop.Name] = append(props, prop)
			}
		}
	}
	var skippedType *Type
	if skipped != nil {
		skippedType = c.getApparentType(skipped)
		if c.isErrorType(skippedType) || skippedType.flags&TypeFlagsNever != 0 {
			skippedType = nil
		}
	}
	// Preserve TypeScript Map insertion order. Iterating byName directly would
	// make property resolution and recursive side effects depend on Go map order.
	for _, name := range names {
		props := byName[name]
		if skippedType != nil {
			prop := c.getPropertyOfTypeEx(skippedType, name, true, false)
			if prop != nil && !slices.Contains(props, prop) {
				props = append(props, prop)
			}
		}
		if len(props) < 2 || !c.someLiteralOrPrivateProperty(props) {
			continue
		}
		combined := c.getPropertyOfUnionOrIntersectionType(t, name, true)
		if combined != nil && c.isNeverReducedProperty(combined) {
			return true
		}
	}
	return false
}

func TestSmallPairReductionMatchesOriginalGrouping(t *testing.T) {
	for _, width := range []int{0, 1, 2, 8, 9, 16} {
		for _, duplicates := range []bool{false, true} {
			for _, optional := range []bool{false, true} {
				for _, conflict := range []bool{false, true} {
					t.Run(fmt.Sprintf("width=%d/duplicate=%v/optional=%v/conflict=%v", width, duplicates, optional, conflict), func(t *testing.T) {
						makeCase := func() (*Checker, *Type) {
							c := lazyPropertyTestChecker()
							a := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
							b := a
							if conflict {
								b = c.newLiteralType(TypeFlagsStringLiteral, "b", nil)
							}
							props := make([]*ast.Symbol, 0, width)
							for i := 0; i < width; i++ {
								name := fmt.Sprintf("p%d", i)
								if duplicates && i == 1 {
									name = "p0"
								}
								props = append(props, lazyProperty(c, name, a, optional))
							}
							left := lazyObject(c, props...)
							// Explicit duplicate-name lists exercise fallback without assuming that
							// every internal caller constructs canonical property arrays.
							left.AsObjectType().properties = props
							rightProps := []*ast.Symbol{lazyProperty(c, "p0", b, optional)}
							for i := 0; i < width+2; i++ {
								rightProps = append(rightProps, lazyProperty(c, fmt.Sprintf("r%d", i), c.numberType, false))
							}
							right := lazyObject(c, rightProps...)
							return c, c.newIntersectionType(ObjectFlagsNone, []*Type{left, right})
						}
						c, intersection := makeCase()
						got := c.hasNeverReducedProperty(intersection)
						reference, original := makeCase()
						want := reference.hasNeverReducedPropertyReference(original)
						if got != want {
							t.Fatalf("candidate=%v original=%v", got, want)
						}
					})
				}
			}
		}
	}
}

func TestSmallPairSharedSymbolDoesNotResolveType(t *testing.T) {
	c := lazyPropertyTestChecker()
	prop := c.newSymbol(ast.SymbolFlagsProperty, "tag")
	left := lazyObject(c, prop)
	right := lazyObject(c, prop, lazyProperty(c, "extra", c.numberType, false))
	intersection := c.newIntersectionType(ObjectFlagsNone, []*Type{left, right})
	if c.hasNeverReducedProperty(intersection) {
		t.Fatal("one symbol cannot conflict with itself")
	}
	if c.valueSymbolLinks.Get(prop).resolvedType != nil {
		t.Fatal("singleton property type was resolved")
	}
}
