package scratch

import (
	"fmt"
	"math/rand"
	"reflect"
	"runtime"
	"slices"
	"testing"
)

type symbol struct {
	value int
	link  *symbol
}

func TestHistories(t *testing.T) {
	var pool Pool[*symbol]
	rng := rand.New(rand.NewSource(42))
	symbols := make([]*symbol, 32)
	for i := range symbols {
		symbols[i] = &symbol{value: i}
	}
	for round := 0; round < 4096; round++ {
		g := pool.Acquire()
		ref := map[string][]*symbol{}
		var names []string
		for j := 0; j < rng.Intn(128)+1; j++ {
			name := fmt.Sprint(rng.Intn(40))
			value := symbols[rng.Intn(len(symbols))]
			vs, ok := ref[name]
			if !ok {
				names = append(names, name)
			}
			if !slices.Contains(vs, value) {
				ref[name] = append(vs, value)
			}
			g.Add(name, value)
		}
		if !reflect.DeepEqual(g.Names(), names) {
			t.Fatal("name order")
		}
		for _, n := range names {
			if !reflect.DeepEqual(g.Values(n), ref[n]) {
				t.Fatal("value identity/order")
			}
		}
		nested := pool.Acquire()
		if nested == g {
			t.Fatal("active storage reused")
		}
		nested.Add("nested", symbols[0])
		pool.Release(nested)
		for _, n := range names {
			if !reflect.DeepEqual(g.Values(n), ref[n]) {
				t.Fatal("recursive mutation")
			}
		}
		pool.Release(g)
		for _, buf := range g.buffers {
			for _, v := range buf[:cap(buf)] {
				if v != nil {
					t.Fatal("retained symbol")
				}
			}
		}
		if len(g.byName) != 0 {
			t.Fatal("retained names")
		}
		for _, n := range g.names[:cap(g.names)] {
			if n != "" {
				t.Fatal("retained name backing")
			}
		}
	}
}
func TestBoundsAndLifetime(t *testing.T) {
	var pool Pool[*symbol]
	g := pool.Acquire()
	first := &symbol{value: 91, link: &symbol{value: 92}}
	g.Add("a", first)
	for i := 0; i < 2048; i++ {
		g.Add(fmt.Sprint(i), &symbol{value: i})
	}
	runtime.GC()
	if g.Values("a")[0] != first || first.link.value != 92 {
		t.Fatal("lifetime")
	}
	pool.Release(g)
	if pool.idle != nil {
		t.Fatal("oversized retained")
	}
	g = pool.Acquire()
	for i := 0; i < 100; i++ {
		g.Add("a", &symbol{value: i})
	}
	pool.Release(g)
	if g.buffers[0] != nil {
		t.Fatal("oversized group retained")
	}
}

var sink int

func BenchmarkGroups(b *testing.B) {
	for _, width := range []int{8, 64, 512} {
		for _, reuse := range []bool{false, true} {
			b.Run(fmt.Sprintf("width%d/reuse%v", width, reuse), func(b *testing.B) {
				names := make([]string, width)
				syms := make([]*symbol, width)
				for i := range names {
					names[i] = fmt.Sprint(i)
					syms[i] = &symbol{value: i}
				}
				var pool Pool[*symbol]
				b.ReportAllocs()
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					if reuse {
						g := pool.Acquire()
						for repeat := 0; repeat < 2; repeat++ {
							for j, n := range names {
								g.Add(n, syms[j])
							}
						}
						sink += len(g.Names())
						pool.Release(g)
					} else {
						m := make(map[string][]*symbol)
						var order []string
						for repeat := 0; repeat < 2; repeat++ {
							for j, n := range names {
								vs, ok := m[n]
								if !ok {
									order = append(order, n)
								}
								if !slices.Contains(vs, syms[j]) {
									m[n] = append(vs, syms[j])
								}
							}
						}
						sink += len(order)
					}
				}
			})
		}
	}
}
