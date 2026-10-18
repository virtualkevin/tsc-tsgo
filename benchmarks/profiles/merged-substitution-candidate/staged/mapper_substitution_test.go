package checker

import (
	"runtime"
	"sync"
	"testing"
	"weak"
)

func legacySubstitutionMap(m *TypeMapper, t *Type) *Type {
	if d, ok := m.data.(*MergedTypeMapper); ok {
		return legacySubstitutionMap(d.m2, legacySubstitutionMap(d.m1, t))
	}
	return m.data.Map(t)
}
func TestMergedSubstitutionExhaustive(t *testing.T) {
	a, b, absent := &Type{}, &Type{}, &Type{}
	domain := []*Type{nil, a, b}
	for encoded := 0; encoded < 6561; encoded++ {
		n := encoded
		var m *TypeMapper
		for i := 0; i < 16; i++ {
			source, target := absent, absent
			if i < 4 {
				pair := n % 9
				n /= 9
				source, target = domain[pair/3], domain[pair%3]
			}
			leaf := newSimpleTypeMapper(source, target)
			if m == nil {
				m = leaf
			} else {
				m = newMergedTypeMapper(m, leaf)
			}
		}
		if m.Kind() != TypeMapperKindMerged || m.data.(*MergedTypeMapper).substitution == nil {
			t.Fatal("missing eligible mapping/kind")
		}
		for _, input := range []*Type{nil, a, b, absent} {
			if m.Map(input) != legacySubstitutionMap(m, input) {
				t.Fatalf("sequence %d", encoded)
			}
		}
	}
}
func TestMergedSubstitutionEligibilityAndEffects(t *testing.T) {
	a, b := &Type{}, &Type{}
	m := newSimpleTypeMapper(a, b)
	for size := 2; size <= 300; size++ {
		m = newMergedTypeMapper(m, newSimpleTypeMapper(b, a))
		d := m.data.(*MergedTypeMapper)
		want := size >= 16 && size <= 256 && size&(size-1) == 0
		if (d.substitution != nil) != want {
			t.Fatalf("size %d", size)
		}
		if m.Map(a) != legacySubstitutionMap(m, a) {
			t.Fatal("chain result")
		}
	}
	calls := 0
	effect := newFunctionTypeMapper(func(t *Type) *Type { calls++; return t })
	mixed := newMergedTypeMapper(m, effect)
	if calls != 0 {
		t.Fatal("construction effects")
	}
	if mixed.data.(*MergedTypeMapper).simpleWeight != 0 || mixed.data.(*MergedTypeMapper).substitution != nil {
		t.Fatal("effectful eligibility")
	}
	mixed.Map(a)
	if calls != 1 {
		t.Fatal("effect skipped")
	}
	targets := []*Type{a}
	array := newArrayTypeMapper([]*Type{b}, targets)
	mixed = newMergedTypeMapper(m, array)
	if mixed.data.(*MergedTypeMapper).substitution != nil {
		t.Fatal("array frozen")
	}
	for _, v := range []*Type{a, b, nil} {
		targets[0] = v
		if mixed.Map(b) != legacySubstitutionMap(mixed, b) {
			t.Fatal("array mutation")
		}
	}
}
func TestMergedSubstitutionConcurrentReads(t *testing.T) {
	var types [33]Type
	m := newSimpleTypeMapper(&types[0], &types[1])
	for i := 1; i < 32; i++ {
		m = newMergedTypeMapper(m, newSimpleTypeMapper(&types[i], &types[i+1]))
	}
	var wg sync.WaitGroup
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 1000; j++ {
				if m.Map(&types[0]) != &types[32] {
					t.Error("result")
				}
			}
		}()
	}
	wg.Wait()
}

//go:noinline
func retainedSubstitutionTree() (*TypeMapper, weak.Pointer[Type]) {
	first, intermediate, last := &Type{}, &Type{}, &Type{}
	m := newMergedTypeMapper(newSimpleTypeMapper(first, intermediate), newSimpleTypeMapper(intermediate, last))
	for i := 2; i < 16; i++ {
		m = newMergedTypeMapper(m, newSimpleTypeMapper(last, last))
	}
	return m, weak.Make(intermediate)
}
func TestMergedSubstitutionOriginalRoots(t *testing.T) {
	m, w := retainedSubstitutionTree()
	runtime.GC()
	runtime.GC()
	if w.Value() == nil {
		t.Fatal("intermediate original root lost")
	}
	runtime.KeepAlive(m)
}
