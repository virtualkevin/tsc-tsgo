package checker

import (
	"fmt"
	"reflect"
	"runtime"
	"testing"
	"weak"
)

func TestMapperPlanPureDifferential(t *testing.T) {
	a, b, c := &Type{}, &Type{}, &Type{}
	sources := []*Type{a, b}
	targets := []*Type{b, c}
	m := newMergedTypeMapper(newArrayTypeMapper(sources, targets), newSimpleTypeMapper(c, a))
	p := compileMapperExecutionPlan(m)
	if p == nil {
		t.Fatal("compile")
	}
	for step := 0; step < 20; step++ {
		// Preserve borrowed leaf-array behavior across repeated queries.
		if step%2 == 0 {
			targets[0] = a
		} else {
			targets[0] = b
		}
		for _, input := range []*Type{a, b, c, nil} {
			if p.Map(input) != m.Map(input) {
				t.Fatalf("step %d", step)
			}
		}
	}
}
func TestMapperPlanStatefulHistory(t *testing.T) {
	run := func(planned bool) ([]string, []int) {
		a, b, c := &Type{id: 1}, &Type{id: 2}, &Type{id: 3}
		var events []string
		step := 0
		leaf := func(name string, fn func(*Type) *Type) *TypeMapper {
			return newFunctionTypeMapper(func(t *Type) *Type { events = append(events, fmt.Sprintf("%s:%d:%d", name, step, t.id)); return fn(t) })
		}
		left := leaf("left", func(t *Type) *Type {
			if step%2 == 0 {
				return b
			}
			return t
		})
		right := leaf("right", func(t *Type) *Type { return c })
		tail := leaf("tail", func(t *Type) *Type { return t })
		m := newMergedTypeMapper(newCompositeTypeMapper(nil, left, right), tail)
		instantiate := func(_ *Checker, t *Type, m *TypeMapper) *Type {
			events = append(events, fmt.Sprintf("instantiate:%d:%d", step, t.id))
			return m.Map(t)
		}
		p := compileMapperExecutionPlan(m)
		if len(events) != 0 {
			t.Fatal("compile executed leaf")
		}
		var outputs []int
		for step = 0; step < 12; step++ {
			var result *Type
			if planned {
				result = p.execute(a, instantiate)
			} else {
				t1 := left.Map(a)
				if t1 != a {
					result = instantiate(nil, t1, right)
				} else {
					result = right.Map(a)
				}
				result = tail.Map(result)
			}
			outputs = append(outputs, int(result.id))
		}
		return events, outputs
	}
	a, b := run(false)
	c, d := run(true)
	if !reflect.DeepEqual(a, c) || !reflect.DeepEqual(b, d) {
		t.Fatalf("history mismatch\n%v\n%v", a, c)
	}
}
func TestMapperPlanFallbackBeforeEffects(t *testing.T) {
	calls := 0
	m := newFunctionTypeMapper(func(t *Type) *Type { calls++; return t })
	for i := 0; i < 300; i++ {
		m = newMergedTypeMapper(m, newSimpleTypeMapper(nil, nil))
	}
	if compileMapperExecutionPlan(m) != nil || calls != 0 {
		t.Fatal("bounded fallback executed effects")
	}
	cycle := &MergedTypeMapper{}
	cycle.data = cycle
	cycle.m1 = &cycle.TypeMapper
	cycle.m2 = newSimpleTypeMapper(nil, nil)
	if compileMapperExecutionPlan(&cycle.TypeMapper) != nil {
		t.Fatal("cycle accepted")
	}
}

//go:noinline
func retainedMapperPlan() (*mapperExecutionPlan, weak.Pointer[Type]) {
	input, target := &Type{}, &Type{}
	return compileMapperExecutionPlan(newSimpleTypeMapper(input, target)), weak.Make(target)
}
func TestMapperPlanTypedLifetime(t *testing.T) {
	p, w := retainedMapperPlan()
	runtime.GC()
	runtime.GC()
	if w.Value() == nil {
		t.Fatal("plan lost leaf target")
	}
	runtime.KeepAlive(p)
}
func BenchmarkMapperPlanMerged(b *testing.B) {
	var ts [33]Type
	m := newSimpleTypeMapper(&ts[0], &ts[1])
	for i := 1; i < 32; i++ {
		m = newMergedTypeMapper(m, newSimpleTypeMapper(&ts[i], &ts[i+1]))
	}
	p := compileMapperExecutionPlan(m)
	b.Run("recursive", func(b *testing.B) {
		b.ReportAllocs()
		for i := 0; i < b.N; i++ {
			if m.Map(&ts[0]) != &ts[32] {
				b.Fatal("result")
			}
		}
	})
	b.Run("plan", func(b *testing.B) {
		b.ReportAllocs()
		for i := 0; i < b.N; i++ {
			if p.Map(&ts[0]) != &ts[32] {
				b.Fatal("result")
			}
		}
	})
}
