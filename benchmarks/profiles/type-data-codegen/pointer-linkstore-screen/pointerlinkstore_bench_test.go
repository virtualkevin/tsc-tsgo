package core

import (
	"fmt"
	"math/rand/v2"
	"runtime"
	"testing"
	"unsafe"
)

// Shape-only substitutes avoid core -> ast -> core. Fields mirror Symbol's
// widths/pointer layout on amd64, without asserting equivalent compiler work.
type pointerBenchSymbol struct {
	flags, checkFlags uint32
	name              string
	declarations      []*pointerBenchSymbol
	valueDeclaration  *pointerBenchSymbol
	members, exports  map[string]*pointerBenchSymbol
	id                uint64
	parent, exported  *pointerBenchSymbol
}

type pointerBenchLinks struct {
	resolved, write, target, mapper, name, containing *pointerBenchSymbol
	checked                                           bool
}

var pointerBenchSum uint64
var pointerBenchLast *pointerBenchLinks

func pointerBenchCheckShape(tb testing.TB) {
	tb.Helper()
	if unsafe.Sizeof(pointerBenchSymbol{}) != 96 || unsafe.Sizeof(pointerBenchLinks{}) != 56 {
		tb.Fatalf("requires 96-byte keys / 56-byte values: got %d/%d", unsafe.Sizeof(pointerBenchSymbol{}), unsafe.Sizeof(pointerBenchLinks{}))
	}
}

func pointerBenchKeys(count int) []*pointerBenchSymbol {
	var arena Arena[pointerBenchSymbol]
	keys := make([]*pointerBenchSymbol, count)
	for i := range keys {
		keys[i] = arena.New()
		keys[i].id = uint64(i + 1)
	}
	return keys
}

func pointerBenchStream(keys []*pointerBenchSymbol, locality bool) []*pointerBenchSymbol {
	stream := append([]*pointerBenchSymbol(nil), keys...)
	rng := rand.New(rand.NewPCG(0x1985, uint64(len(keys))))
	rng.Shuffle(len(stream), func(i, j int) { stream[i], stream[j] = stream[j], stream[i] })
	if locality {
		// 90% of accesses target the same 64 randomly selected keys. The
		// remaining 10% sample the full populated store. This is a synthetic
		// locality screen, not an asserted compiler access distribution.
		hot := append([]*pointerBenchSymbol(nil), stream[:64]...)
		for i := range stream {
			if rng.IntN(10) != 0 {
				stream[i] = hot[rng.IntN(len(hot))]
			}
		}
	}
	return stream
}

func BenchmarkPointerLinkStoreHits(b *testing.B) {
	pointerBenchCheckShape(b)
	for _, population := range []int{4096, 65536, 1 << 20} {
		b.Run(fmt.Sprintf("n=%d", population), func(b *testing.B) {
			keys := pointerBenchKeys(population)
			for _, locality := range []bool{false, true} {
				name := "shuffled"
				if locality {
					name = "locality90"
				}
				stream := pointerBenchStream(keys, locality)
				mask := len(stream) - 1
				b.Run(name, func(b *testing.B) {
					b.Run("map", func(b *testing.B) {
						var store LinkStore[*pointerBenchSymbol, pointerBenchLinks]
						for _, key := range keys {
							store.New(key).target = key
						}
						runtime.GC()
						b.ReportAllocs()
						b.ResetTimer()
						var sum uint64
						for i := 0; i < b.N; i++ {
							sum += store.Get(stream[i&mask]).target.id
						}
						b.StopTimer()
						pointerBenchSum = sum
						runtime.KeepAlive(store)
					})
					b.Run("pointer", func(b *testing.B) {
						var store PointerLinkStore[pointerBenchSymbol, pointerBenchLinks]
						for _, key := range keys {
							store.New(key).target = key
						}
						runtime.GC()
						b.ReportAllocs()
						b.ResetTimer()
						var sum uint64
						for i := 0; i < b.N; i++ {
							sum += store.Get(stream[i&mask]).target.id
						}
						b.StopTimer()
						pointerBenchSum = sum
						runtime.KeepAlive(store)
					})
				})
			}
		})
	}
}

// Construction is deliberately separate: each benchmark op builds one entire
// table, including arena/table growth. ns/op and allocations/op are per table.
func BenchmarkPointerLinkStoreConstruction(b *testing.B) {
	pointerBenchCheckShape(b)
	for _, population := range []int{4096, 65536, 1 << 20} {
		b.Run(fmt.Sprintf("n=%d", population), func(b *testing.B) {
			keys := pointerBenchKeys(population)
			b.Run("map", func(b *testing.B) {
				b.ReportAllocs()
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					var store LinkStore[*pointerBenchSymbol, pointerBenchLinks]
					var last *pointerBenchLinks
					for _, key := range keys {
						last = store.New(key)
					}
					pointerBenchLast = last
					runtime.KeepAlive(store)
				}
				b.StopTimer()
				b.ReportMetric(float64(b.Elapsed().Nanoseconds())/float64(b.N)/float64(population), "ns/key")
			})
			b.Run("pointer", func(b *testing.B) {
				b.ReportAllocs()
				b.ResetTimer()
				for i := 0; i < b.N; i++ {
					var store PointerLinkStore[pointerBenchSymbol, pointerBenchLinks]
					var last *pointerBenchLinks
					for _, key := range keys {
						last = store.New(key)
					}
					pointerBenchLast = last
					runtime.KeepAlive(store)
				}
				b.StopTimer()
				b.ReportMetric(float64(b.Elapsed().Nanoseconds())/float64(b.N)/float64(population), "ns/key")
			})
		})
	}
}

func TestPointerLinkStoreBenchHitAllocations(t *testing.T) {
	pointerBenchCheckShape(t)
	keys := pointerBenchKeys(4096)
	stream := pointerBenchStream(keys, false)
	var mapped LinkStore[*pointerBenchSymbol, pointerBenchLinks]
	var pointer PointerLinkStore[pointerBenchSymbol, pointerBenchLinks]
	for _, key := range keys {
		mapped.New(key).target = key
		pointer.New(key).target = key
	}
	// AllocsPerRun invokes a batch closure, not a per-Get callback. This is
	// solely an allocation assertion, separate from benchmark timing loops.
	if allocations := testing.AllocsPerRun(10, func() {
		var sum uint64
		for _, key := range stream {
			sum += mapped.Get(key).target.id
		}
		pointerBenchSum = sum
	}); allocations != 0 {
		t.Fatalf("map hit batch allocated %g objects", allocations)
	}
	if allocations := testing.AllocsPerRun(10, func() {
		var sum uint64
		for _, key := range stream {
			sum += pointer.Get(key).target.id
		}
		pointerBenchSum = sum
	}); allocations != 0 {
		t.Fatalf("pointer-table hit batch allocated %g objects", allocations)
	}
}
