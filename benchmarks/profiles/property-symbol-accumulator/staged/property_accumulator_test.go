package checker

import (
	"slices"
	"testing"
)

func TestPropertyAccumulatorQueryOrder(t *testing.T) {
	for _, width := range []int{1, 2, 3, 16, 17, 32} {
		c := lazyPropertyTestChecker()
		parameter := c.newTypeParameter(nil)
		var observed []int
		objects := make([]*Type, width)
		for i := range objects {
			original := lazyProperty(c, "value", parameter, false)
			mapper := newFunctionTypeMapper(func(input *Type) *Type {
				if input == parameter {
					observed = append(observed, i)
					return c.stringType
				}
				return input
			})
			objects[i] = lazyObject(c, c.newInstantiatedSymbol(original, mapper))
		}
		// Repeated exact symbols interleaved with distinct symbols must not repeat
		// queries or reorder their first occurrences, even across map promotion.
		var constituents []*Type
		var want []int
		for i := width - 1; i >= 0; i-- {
			constituents = append(constituents, objects[i], objects[i])
			if i < width-1 {
				constituents = append(constituents, objects[width-1])
			}
			want = append(want, i)
		}
		typ := c.newUnionType(ObjectFlagsNone, constituents)
		prop := c.getUnionOrIntersectionProperty(typ, "value", true)
		if prop == nil {
			t.Fatal("missing synthesized property")
		}
		_ = c.getTypeOfSymbol(prop)
		if !slices.Equal(observed, want) {
			t.Fatalf("width %d: queries %v, want %v", width, observed, want)
		}
		if c.getUnionOrIntersectionProperty(typ, "value", false) != prop {
			t.Fatal("lost published identity")
		}
		if !slices.Equal(observed, want) {
			t.Fatal("cache hit repeated semantic queries")
		}
	}
}
