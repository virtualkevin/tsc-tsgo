package checker

import (
	"runtime"
	"testing"
)

func TestMapperPairOrderAndStructure(t *testing.T) {
	c := activeMapperTestChecker()
	a, b, d := c.newTypeParameter(nil), c.newTypeParameter(nil), c.newTypeParameter(nil)
	for _, prepend := range []bool{false, true} {
		var seen []*Type
		other := newFunctionTypeMapper(func(x *Type) *Type {
			seen = append(seen, x)
			if x == b {
				return d
			}
			return x
		})
		var got, old *TypeMapper
		if prepend {
			got = prependTypeMapping(a, b, other)
			old = newMergedTypeMapper(newSimpleTypeMapper(a, b), other)
		} else {
			got = appendTypeMapping(other, a, b)
			old = newMergedTypeMapper(other, newSimpleTypeMapper(a, b))
		}
		if got.Kind() != TypeMapperKindMerged || got.MapsThisOnly() || compareTypeMappers(got, old) != 0 {
			t.Fatal("mapper structure changed")
		}
		for _, input := range []*Type{a, b, d} {
			seen = nil
			want := old.Map(input)
			wantSeen := seen[0]
			seen = nil
			actual := got.Map(input)
			if actual != want || len(seen) != 1 || seen[0] != wantSeen {
				t.Fatal("mapping order or callback count changed")
			}
		}
		merged := got.data.(*MergedTypeMapper)
		child := merged.m2
		if prepend {
			child = merged.m1
		}
		if child.Kind() != TypeMapperKindSimple || child.Map(a) != b {
			t.Fatal("child representation changed")
		}
		runtime.GC()
		if got.Map(a) != old.Map(a) || child.Map(a) != b {
			t.Fatal("pair lost roots across GC")
		}
	}
}

func TestMapperPairNilAndDistinctIdentity(t *testing.T) {
	c := activeMapperTestChecker()
	a, b := c.newTypeParameter(nil), c.newTypeParameter(nil)
	for _, m := range []*TypeMapper{prependTypeMapping(a, b, nil), appendTypeMapping(nil, a, b)} {
		if m.Kind() != TypeMapperKindSimple || m.Map(a) != b || m.Map(b) != b {
			t.Fatal("nil mapper behavior changed")
		}
	}
	other := newSimpleTypeMapper(b, a)
	first, second := appendTypeMapping(other, a, b), appendTypeMapping(other, a, b)
	if first == second || first.data.(*MergedTypeMapper).m2 == second.data.(*MergedTypeMapper).m2 {
		t.Fatal("independent mapper identities aliased")
	}
	if first.data.(*MergedTypeMapper).m1 != other {
		t.Fatal("existing mapper copied")
	}
}

var mapperPairSink *TypeMapper

func TestMapperPairAllocations(t *testing.T) {
	c := activeMapperTestChecker()
	a, b := c.newTypeParameter(nil), c.newTypeParameter(nil)
	other := newSimpleTypeMapper(b, a)
	for _, prepend := range []bool{false, true} {
		allocations := testing.AllocsPerRun(1000, func() {
			if prepend {
				mapperPairSink = prependTypeMapping(a, b, other)
			} else {
				mapperPairSink = appendTypeMapping(other, a, b)
			}
		})
		if allocations != 1 {
			t.Fatalf("pair allocations = %g, want 1", allocations)
		}
	}
	mapperPairSink = nil
}
