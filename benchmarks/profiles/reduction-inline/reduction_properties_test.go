package checker

import (
	"fmt"
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func TestReductionPropertiesRepeatedSymbolDoesNotResolveType(t *testing.T) {
	c := lazyPropertyTestChecker()
	// Resolving this symbol without a declaration or cached type is invalid.
	// Repeated contributions of one symbol must still be treated as a singleton.
	prop := c.newSymbol(ast.SymbolFlagsProperty, "tag")
	intersection := c.newIntersectionType(ObjectFlagsNone, []*Type{lazyObject(c, prop), lazyObject(c, prop), lazyObject(c, prop)})
	if c.hasNeverReducedProperty(intersection) {
		t.Fatal("one symbol cannot conflict with itself")
	}
	if c.valueSymbolLinks.Get(prop).resolvedType != nil {
		t.Fatal("singleton type was resolved")
	}
}

func TestReductionPropertiesMultipleConstituentsMatchEager(t *testing.T) {
	for _, optional := range []bool{false, true} {
		for _, conflicting := range []bool{false, true} {
			for first := 0; first < 4; first++ {
				for second := 0; second < 4; second++ {
					if first == second {
						continue
					}
					for third := 0; third < 4; third++ {
						if third == first || third == second {
							continue
						}
						fourth := 6 - first - second - third
						t.Run(fmt.Sprintf("optional=%v/conflict=%v/order=%d%d%d%d", optional, conflicting, first, second, third, fourth), func(t *testing.T) {
							c := lazyPropertyTestChecker()
							a := c.newLiteralType(TypeFlagsStringLiteral, "a", nil)
							b := a
							if conflicting {
								b = c.newLiteralType(TypeFlagsStringLiteral, "b", nil)
							}
							shared := lazyProperty(c, "tag", a, optional)
							objects := []*Type{
								lazyObject(c, shared),
								lazyObject(c, shared, lazyProperty(c, "x", c.numberType, false)),
								lazyObject(c, lazyProperty(c, "tag", a, optional)),
								lazyObject(c, lazyProperty(c, "tag", b, optional), lazyProperty(c, "y", c.numberType, false)),
							}
							intersection := c.newIntersectionType(ObjectFlagsNone, []*Type{objects[first], objects[second], objects[third], objects[fourth]})
							got := c.hasNeverReducedProperty(intersection)
							want := false
							for _, prop := range c.getPropertiesOfUnionOrIntersectionType(intersection) {
								if c.isNeverReducedProperty(prop) {
									want = true
									break
								}
							}
							if got != want {
								t.Fatalf("lazy=%v eager=%v", got, want)
							}
							if got != (!optional && conflicting) {
								t.Fatalf("unexpected reduction: %v", got)
							}
						})
					}
				}
			}
		}
	}
}
