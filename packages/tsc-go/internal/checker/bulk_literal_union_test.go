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

func TestMergeLiteralRunsMatchesInsertion(t *testing.T) {
	c := &Checker{strictNullChecks: true}
	keys := make([]*Type, 120)
	for i := range keys {
		keys[i] = c.newLiteralType(TypeFlagsStringLiteral, fmt.Sprintf("%03d", i), nil)
	}
	set := slices.Clone(keys[40:80])
	set = append(set, c.newIntrinsicType(TypeFlagsNumber, "number"), c.getFreshTypeOfLiteralType(keys[60]))
	slices.SortFunc(set, CompareTypes)
	for _, run := range [][]*Type{keys[:40], keys[80:], keys[20:60], keys[40:80], keys[60:100], keys[20:100]} {
		input := slices.Clone(run)
		union := c.newUnionType(ObjectFlagsPrimitiveUnion, run)
		got, flags := c.addTypesToUnion(slices.Clone(set), TypeFlagsNumber, []*Type{union})
		want := slices.Clone(set)
		for _, v := range run {
			want, _ = c.addTypeToUnion(want, 0, v)
		}
		if !slices.Equal(got, want) || flags != TypeFlagsStringLiteral|TypeFlagsNumber || !slices.Equal(run, input) {
			t.Fatal("sorted literal run differs from per-element insertion")
		}
	}
	for _, invalid := range [][]*Type{{keys[1], keys[0]}, {keys[0], keys[0]}, {keys[0], nil}} {
		if c.isSortedStringLiteralRun(invalid) {
			t.Fatal("invalid literal run accepted")
		}
	}
}
