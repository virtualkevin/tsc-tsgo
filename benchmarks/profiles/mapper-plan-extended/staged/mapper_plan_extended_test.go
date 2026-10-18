package checker

import (
	"fmt"
	"math/rand"
	"reflect"
	"testing"
)

// Independent recursive control-flow oracle; effectful leaves are unchanged.
func mapperPlanReference(m *TypeMapper, t *Type, instantiate mapperPlanInstantiate) *Type {
	switch d := m.data.(type) {
	case *MergedTypeMapper:
		return mapperPlanReference(d.m2, mapperPlanReference(d.m1, t, instantiate), instantiate)
	case *CompositeTypeMapper:
		t1 := mapperPlanReference(d.m1, t, instantiate)
		if t1 != t {
			return instantiate(d.c, t1, d.m2)
		}
		return mapperPlanReference(d.m2, t, instantiate)
	default:
		return m.data.Map(t)
	}
}
func TestMapperPlanNestedHistoriesAndPanics(t *testing.T) {
	run := func(seed int64, planned bool) ([]string, []string) {
		rng := rand.New(rand.NewSource(seed))
		types := []*Type{{id: 1}, {id: 2}, {id: 3}, {id: 4}}
		var trace, results []string
		calls, step, nextLeaf := 0, 0, 0
		var graph func(int) *TypeMapper
		graph = func(depth int) *TypeMapper {
			if depth == 0 || rng.Intn(4) == 0 {
				id := nextLeaf
				nextLeaf++
				return newFunctionTypeMapper(func(input *Type) *Type {
					calls++
					trace = append(trace, fmt.Sprintf("leaf:%d:%d:%d:%d", step, id, input.id, calls))
					if calls%17 == 0 {
						panic("fixture failure")
					}
					if (step+id)%3 == 0 {
						return input
					}
					return types[(int(input.id)+id+step)%len(types)]
				})
			}
			left, right := graph(depth-1), graph(depth-1)
			if rng.Intn(2) == 0 {
				return newMergedTypeMapper(left, right)
			}
			return newCompositeTypeMapper(nil, left, right)
		}
		m := graph(5)
		p := compileMapperExecutionPlan(m)
		if p == nil {
			t.Fatalf("seed %d did not compile", seed)
		}
		if len(trace) != 0 {
			t.Fatal("compilation effects")
		}
		var instantiate mapperPlanInstantiate
		instantiate = func(_ *Checker, input *Type, m *TypeMapper) *Type {
			trace = append(trace, fmt.Sprintf("instantiate:%d:%d", step, input.id))
			return mapperPlanReference(m, input, instantiate)
		}
		for step = 0; step < 24; step++ {
			func() {
				defer func() {
					if r := recover(); r != nil {
						results = append(results, fmt.Sprintf("panic:%v", r))
					}
				}()
				input := types[step%len(types)]
				var result *Type
				if planned {
					result = p.execute(input, instantiate)
				} else {
					result = mapperPlanReference(m, input, instantiate)
				}
				results = append(results, fmt.Sprintf("type:%d", result.id))
			}()
		}
		return trace, results
	}
	for seed := int64(0); seed < 128; seed++ {
		a, b := run(seed, false)
		c, d := run(seed, true)
		if !reflect.DeepEqual(a, c) || !reflect.DeepEqual(b, d) {
			t.Fatalf("seed %d: trace/result mismatch\n%v\n%v\n%v\n%v", seed, a, c, b, d)
		}
	}
}

var mapperPlanBenchmarkSink *mapperExecutionPlan

func BenchmarkMapperPlanCosts(b *testing.B) {
	for _, n := range []int{1, 2, 4, 8, 32} {
		b.Run(fmt.Sprint(n), func(b *testing.B) {
			types := make([]Type, n+1)
			m := newSimpleTypeMapper(&types[0], &types[1])
			for i := 1; i < n; i++ {
				m = newMergedTypeMapper(m, newSimpleTypeMapper(&types[i], &types[i+1]))
			}
			p := compileMapperExecutionPlan(m)
			b.Run("recursive", func(b *testing.B) {
				b.ReportAllocs()
				for i := 0; i < b.N; i++ {
					if m.Map(&types[0]) != &types[n] {
						b.Fatal("result")
					}
				}
			})
			b.Run("plan", func(b *testing.B) {
				b.ReportAllocs()
				for i := 0; i < b.N; i++ {
					if p.Map(&types[0]) != &types[n] {
						b.Fatal("result")
					}
				}
			})
			b.Run("compile", func(b *testing.B) {
				b.ReportAllocs()
				for i := 0; i < b.N; i++ {
					mapperPlanBenchmarkSink = compileMapperExecutionPlan(m)
				}
			})
		})
	}
}
