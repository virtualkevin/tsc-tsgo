package core

import (
	"fmt"
	"math/rand/v2"
	"runtime"
	"sync"
	"testing"
	"unsafe"
	"weak"
)

type denseKey struct{ words [12]uint64 }
type denseValue struct{ refs [7]*denseKey }

func TestDensePointerLinksDifferential(t *testing.T) {
	var got DensePointerLinks[denseKey, denseValue]
	var want PointerLinkStore[denseKey, denseValue]
	keys := make([]*denseKey, 4097)
	var arena Arena[denseKey]
	for i := 1; i < len(keys); i++ {
		keys[i] = arena.New()
		keys[i].words[0] = uint64(i)
	}
	rng := rand.New(rand.NewPCG(77, 12))
	published := map[*denseKey]*denseValue{}
	for step := range 40000 {
		key := keys[rng.IntN(len(keys))]
		switch rng.IntN(4) {
		case 0, 1:
			a, b := got.Get(key), want.Get(key)
			if old := published[key]; old != nil && old != a {
				t.Fatal("Get identity changed")
			}
			if *a != *b {
				t.Fatal("value mismatch")
			}
			a.refs[0], b.refs[0] = keys[step%len(keys)], keys[step%len(keys)]
			published[key] = a
		case 2:
			old := got.TryGet(key)
			var previous denseValue
			if old != nil {
				previous = *old
			}
			a, b := got.New(key), want.New(key)
			if a == old || *a != (denseValue{}) || *a != *b || old != nil && *old != previous {
				t.Fatal("replacement")
			}
			published[key] = a
		case 3:
			a, b := got.TryGet(key), want.TryGet(key)
			if got.Has(key) != want.Has(key) || (a == nil) != (b == nil) || a != nil && *a != *b {
				t.Fatal("lookup")
			}
		}
	}
	runtime.GC()
	runtime.GC()
	if len(got.entries) != want.count {
		t.Fatal("duplicate root or lost key")
	}
	for key, value := range published {
		if got.Get(key) != value {
			t.Fatal("growth identity")
		}
	}
	// At matched table capacities both payloads nominally use16B/bucket, but
	// dense roots contain25%fewer pointer slots. Excludes headers/allocator size.
	if len(got.slots) != len(want.entries) || cap(got.entries) != len(got.slots)*3/4 {
		t.Fatal("capacity policy")
	}
	if unsafe.Sizeof(pointerLinkEntry[denseKey, denseValue]{}) == 16 && cap(got.entries)*16+len(got.slots)*4 != len(want.entries)*16 {
		t.Fatal("layout accounting")
	}
}

//go:noinline
func densePopulate() (DensePointerLinks[denseKey, denseValue], weak.Pointer[denseKey], *denseValue) {
	var s DensePointerLinks[denseKey, denseValue]
	var keys Arena[denseKey]
	first := keys.New()
	first.words[0] = 42
	old := s.Get(first)
	old.refs[0] = new(denseKey)
	old.refs[0].words[0] = 73
	s.New(first)
	for i := range 4096 {
		key := keys.New()
		key.words[0] = uint64(i)
		s.Get(key).refs[0] = key
	}
	return s, weak.Make(first), old
}
func TestDensePointerLinksLifetime(t *testing.T) {
	s, w, old := densePopulate()
	runtime.GC()
	runtime.GC()
	key := w.Value()
	if key == nil || key.words[0] != 42 || s.TryGet(key) == nil || s.TryGet(key) == old || old.refs[0].words[0] != 73 {
		t.Fatal("lost roots or published value")
	}
	for _, entry := range s.entries {
		if s.TryGet(entry.key) != entry.value {
			t.Fatal("displaced key lost")
		}
	}
	runtime.KeepAlive(s)
}
func TestDensePointerLinksConcurrentReads(t *testing.T) {
	s, _, _ := densePopulate()
	copyStore := s
	var group sync.WaitGroup
	for range 8 {
		group.Go(func() {
			for _, entry := range copyStore.entries {
				if s.Get(entry.key) != entry.value || copyStore.TryGet(entry.key) != entry.value {
					t.Error("read identity")
				}
			}
		})
	}
	group.Wait()
}
func TestDensePointerLinksNilAndCollision(t *testing.T) {
	var s DensePointerLinks[denseKey, denseValue]
	if s.Has(nil) || s.slots != nil {
		t.Fatal("empty read")
	}
	a := s.Get(nil)
	a.refs[0] = new(denseKey)
	if s.Get(nil) != a || s.New(nil) == a || len(s.entries) != 1 {
		t.Fatal("nil replacement")
	}
	keys := make([]denseKey, 1024)
	var buckets [16][]*denseKey
	for i := range keys {
		b := pointerLinkHash(&keys[i]) & 15
		buckets[b] = append(buckets[b], &keys[i])
	}
	for _, bucket := range buckets {
		if len(bucket) >= 64 {
			for _, key := range bucket {
				s.Get(key).refs[0] = key
			}
			for _, key := range bucket {
				if s.TryGet(key).refs[0] != key {
					t.Fatal("collision growth")
				}
			}
			return
		}
	}
	t.Fatal("pigeonhole failed")
}
func BenchmarkDensePointerLinksLookup(b *testing.B) {
	for _, size := range []int{256, 65536} {
		b.Run(fmt.Sprint(size), func(b *testing.B) {
			keys := make([]denseKey, size)
			var dense DensePointerLinks[denseKey, denseValue]
			var pointer PointerLinkStore[denseKey, denseValue]
			for i := range keys {
				key := &keys[i]
				dense.Get(key).refs[0] = key
				pointer.Get(key).refs[0] = key
			}
			b.Run("pointer", func(b *testing.B) {
				i := 0
				for b.Loop() {
					i = (i + 7919) & (size - 1)
					if pointer.Get(&keys[i]).refs[0] != &keys[i] {
						b.Fatal("value")
					}
				}
			})
			b.Run("dense", func(b *testing.B) {
				i := 0
				for b.Loop() {
					i = (i + 7919) & (size - 1)
					if dense.Get(&keys[i]).refs[0] != &keys[i] {
						b.Fatal("value")
					}
				}
			})
		})
	}
}
