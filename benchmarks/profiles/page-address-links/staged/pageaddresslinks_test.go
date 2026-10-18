package core

import (
	"fmt"
	"math/rand/v2"
	"runtime"
	"sync"
	"testing"
	"weak"
)

type pageAddressKey struct{ words [12]uint64 }
type pageAddressValue struct{ refs [7]*pageAddressKey }

func TestPageAddressLinksDifferential(t *testing.T) {
	var got PageAddressLinks[pageAddressKey, pageAddressValue]
	var foreign PageAddressLinks[pageAddressKey, pageAddressValue]
	var want PointerLinkStore[pageAddressKey, pageAddressValue]
	keys := []*pageAddressKey{nil, new(pageAddressKey), foreign.NewKey()}
	for range 4097 {
		keys = append(keys, got.NewKey())
	}
	for _, key := range keys {
		if got.Has(key) {
			t.Fatal("allocation created links")
		}
	}
	rng := rand.New(rand.NewPCG(112, 83))
	old := map[*pageAddressKey]*pageAddressValue{}
	for step := range 30000 {
		key := keys[rng.IntN(len(keys))]
		switch rng.IntN(4) {
		case 0, 1:
			a, b := got.Get(key), want.Get(key)
			if p := old[key]; p != nil && a != p {
				t.Fatal("Get identity")
			}
			if *a != *b {
				t.Fatal("value mismatch")
			}
			a.refs[0], b.refs[0] = keys[(step+1)%len(keys)], keys[(step+1)%len(keys)]
			old[key] = a
		case 2:
			previous := got.TryGet(key)
			var saved pageAddressValue
			if previous != nil {
				saved = *previous
			}
			a, b := got.New(key), want.New(key)
			if *a != *b || *a != (pageAddressValue{}) || previous == a {
				t.Fatal("replacement")
			}
			if previous != nil && *previous != saved {
				t.Fatal("old published value changed")
			}
			old[key] = a
		case 3:
			a, b := got.TryGet(key), want.TryGet(key)
			if (a == nil) != (b == nil) || a != nil && *a != *b || got.Has(key) != (b != nil) {
				t.Fatal("lookup")
			}
		}
	}
	runtime.GC()
	runtime.GC()
	for key, value := range old {
		if got.Get(key) != value {
			t.Fatal("growth/GC identity")
		}
	}
	if len(got.roots) > len(keys)-3 {
		t.Fatal("duplicate roots")
	}
}

//go:noinline
func pageAddressUnlinked() (PageAddressLinks[pageAddressKey, pageAddressValue], weak.Pointer[pageAddressKey]) {
	var store PageAddressLinks[pageAddressKey, pageAddressValue]
	key := store.NewKey()
	w := weak.Make(key)
	for range 256 {
		store.NewKey()
	}
	return store, w
}

func TestPageAddressLinksUnlinkedLifetime(t *testing.T) {
	store, w := pageAddressUnlinked()
	for range 10 {
		runtime.GC()
		if w.Value() == nil {
			break
		}
	}
	if w.Value() != nil {
		t.Fatal("directory retained an unlinked displaced key page")
	}
	runtime.KeepAlive(store)
}

//go:noinline
func pageAddressLinked() (PageAddressLinks[pageAddressKey, pageAddressValue], weak.Pointer[pageAddressKey], *pageAddressValue) {
	var store PageAddressLinks[pageAddressKey, pageAddressValue]
	key := store.NewKey()
	key.words[0] = 42
	old := store.Get(key)
	old.refs[0] = new(pageAddressKey)
	old.refs[0].words[0] = 73
	store.New(key)
	for range 4096 {
		store.NewKey()
	}
	return store, weak.Make(key), old
}

func TestPageAddressLinksLinkedLifetime(t *testing.T) {
	store, w, old := pageAddressLinked()
	runtime.GC()
	runtime.GC()
	key := w.Value()
	if key == nil || key.words[0] != 42 || store.TryGet(key) == nil || store.TryGet(key) == old || old.refs[0].words[0] != 73 {
		t.Fatal("linked key or published value lost")
	}
	if len(store.roots) != 1 {
		t.Fatal("replacement duplicated root")
	}
	runtime.KeepAlive(store)
}

func TestPageAddressLinksConcurrentReads(t *testing.T) {
	var store PageAddressLinks[pageAddressKey, pageAddressValue]
	keys := make([]*pageAddressKey, 1025)
	for i := range keys {
		keys[i] = store.NewKey()
		store.Get(keys[i]).refs[0] = keys[i]
	}
	copyStore := store
	var group sync.WaitGroup
	for range 8 {
		group.Go(func() {
			for i := range 4000 {
				key := keys[i%len(keys)]
				if copyStore.Get(key).refs[0] != key || !store.Has(key) {
					t.Error("read mismatch")
					return
				}
			}
		})
	}
	group.Wait()
}

func TestPageAddressLinksRegionBoundaries(t *testing.T) {
	// One page spans many directory regions; every element must be registered.
	type huge struct{ bytes [1025]byte }
	var store PageAddressLinks[huge, int]
	for i := range 257 {
		key := store.NewKey()
		*store.Get(key) = i
		page, index := store.locate(key)
		if page == nil || *page.values[index] != i {
			t.Fatal("region boundary")
		}
	}
	var zero PageAddressLinks[struct{}, int]
	key := zero.NewKey()
	*zero.Get(key) = 17
	if *zero.TryGet(key) != 17 {
		t.Fatal("zero-sized fallback")
	}
}

func BenchmarkPageAddressLinksLookup(b *testing.B) {
	for _, size := range []int{256, 65536} {
		b.Run(fmt.Sprint(size), func(b *testing.B) {
			var pages PageAddressLinks[pageAddressKey, pageAddressValue]
			var pointers PointerLinkStore[pageAddressKey, pageAddressValue]
			keys := make([]*pageAddressKey, size)
			for i := range keys {
				keys[i] = pages.NewKey()
				pages.Get(keys[i]).refs[0] = keys[i]
				pointers.Get(keys[i]).refs[0] = keys[i]
			}
			b.Run("pointer", func(b *testing.B) {
				i := 0
				for b.Loop() {
					i = (i + 7919) & (size - 1)
					if pointers.Get(keys[i]).refs[0] != keys[i] {
						b.Fatal("value")
					}
				}
			})
			b.Run("page", func(b *testing.B) {
				i := 0
				for b.Loop() {
					i = (i + 7919) & (size - 1)
					if pages.Get(keys[i]).refs[0] != keys[i] {
						b.Fatal("value")
					}
				}
			})
			runtime.KeepAlive(keys)
		})
	}
}
