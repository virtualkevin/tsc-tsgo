package checker

import (
	"fmt"
	"slices"
	"testing"
)

func TestTemplateUnionCompactionPreservesSurvivors(t *testing.T) {
	c := templateCacheTestChecker()
	pattern := c.newTemplateLiteralType([]string{"", "yes"}, []*Type{c.stringType})
	// All 256 subsets include prefix, suffix, interior and alternating removals.
	for mask := range 256 {
		types := []*Type{pattern}
		var want []*Type
		for i := range 8 {
			suffix := "no"
			if mask&(1<<i) != 0 {
				suffix = "yes"
			}
			typ := c.getStringLiteralType(fmt.Sprintf("%d%s", i, suffix))
			types = append(types, typ)
			if suffix == "no" {
				want = append(want, typ)
			}
		}
		slices.SortFunc(types, CompareTypes)
		want = append(want, pattern)
		slices.SortFunc(want, CompareTypes)
		got := c.removeStringLiteralsMatchedByTemplateLiterals(types)
		if !slices.Equal(got, want) {
			t.Fatalf("mask %08b changed surviving type identity or order", mask)
		}
		for _, typ := range types[len(got):] {
			if typ != nil {
				t.Fatalf("mask %08b retained a discarded tail pointer", mask)
			}
		}
	}
}
