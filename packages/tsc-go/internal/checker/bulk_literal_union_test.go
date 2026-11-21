package checker

import (
	"fmt"
	"slices"
	"testing"
)

func TestBulkLiteralUnionMatchesOrderedInsertion(t *testing.T) {
	c := &Checker{strictNullChecks: true}
	regular := c.newLiteralType(TypeFlagsStringLiteral, "equal", nil)
	fresh := c.getFreshTypeOfLiteralType(regular)
	base := []*Type{regular, fresh, regular}
	for i := 30; i >= 0; i-- {
		base = append(base, c.newLiteralType(TypeFlagsStringLiteral, fmt.Sprintf("%02d", i), nil))
	}
	base = append(base, fresh)
	for _, size := range []int{15, 16, len(base)} {
		values := slices.Clone(base[:size])
		input := slices.Clone(values)
		initial := TypeFlagsIncludesConstrainedTypeVariable
		got, flags := c.addTypesToUnion(nil, initial, values)
		var want []*Type
		wantFlags := initial
		for _, v := range values {
			want, wantFlags = c.addTypeToUnion(want, wantFlags, v)
		}
		if !slices.Equal(got, want) || flags != wantFlags || !slices.Equal(values, input) {
			t.Fatalf("union with %d inputs differs from ordered insertion", size)
		}
	}
}
