package core

import (
	"runtime"
	"sync"
	"testing"
)

type indexedTestKey struct {
	n    int
	tail *[64]int
}
type indexedTestValue struct {
	n    int
	tail *[64]int
}

func TestIndexedPointerLinksBoundariesIdentityAndReplacement(t *testing.T) {
	var store IndexedPointerLinkStore[indexedTestKey, indexedTestValue]
	indices := []uint32{0, 1, 255, 256, 65535, 65536, 16777215, 16777216, ^uint32(0)}
	keys := make([]*indexedTestKey, len(indices))
	values := make([]*indexedTestValue, len(indices))
	for i, index := range indices {
		keys[i] = &indexedTestKey{n: i}
		values[i] = store.Get(keys[i], index)
		values[i].n = i + 1
	}
	for i, index := range indices {
		if store.Get(keys[i], index) != values[i] || store.TryGet(keys[i], index) != values[i] || !store.Has(keys[i], index) {
			t.Fatalf("lookup changed at %x", index)
		}
		next := store.New(keys[i], index)
		if next == values[i] || next.n != 0 || values[i].n != i+1 {
			t.Fatalf("replacement lost identity/old value at %x", index)
		}
	}
	// A copied allocation handle never makes distinct pointer keys equivalent.
	original, copied := &indexedTestKey{n: 100}, &indexedTestKey{n: 101}
	a, b := store.Get(original, 42), store.Get(copied, 42)
	a.n = 100
	b.n = 101
	if a == b || store.Get(original, 42) != a || store.Get(copied, 42) != b {
		t.Fatal("handle collision aliased pointer identities")
	}
	old := store.New(copied, 42)
	if old == b || b.n != 101 || store.Get(original, 42) != a {
		t.Fatal("fallback replacement changed indexed entry")
	}
	nilValue := store.Get(nil, 0)
	nilValue.n = 999
	if store.TryGet(nil, 0) != nilValue {
		t.Fatal("nil-key fallback lost value")
	}
}

func TestIndexedPointerLinksReadonlyMissesAndReaders(t *testing.T) {
	var store IndexedPointerLinkStore[indexedTestKey, indexedTestValue]
	keys := []*indexedTestKey{{n: 1}, {n: 2}, {n: 3}}
	indices := []uint32{1, 1, 0} // indexed, colliding-handle fallback, unindexed fallback
	for i, k := range keys {
		store.Get(k, indices[i]).n = i + 1
	}
	rootBefore := store.root
	var readers sync.WaitGroup
	for range 8 {
		readers.Go(func() {
			for range 100 {
				for i, k := range keys {
					if store.Get(k, indices[i]).n != i+1 || store.TryGet(k, indices[i]).n != i+1 {
						t.Error("published read changed")
					}
				}
				if store.TryGet(nil, ^uint32(0)) != nil || store.Has(nil, ^uint32(0)) {
					t.Error("missing key found")
				}
			}
		})
	}
	readers.Wait()
	if store.root != rootBefore {
		t.Fatal("read-only lookup allocated radix metadata")
	}
	var empty IndexedPointerLinkStore[indexedTestKey, indexedTestValue]
	if empty.Has(nil, 0) || empty.TryGet(nil, 0) != nil || len(empty.fallback.entries) != 0 {
		t.Fatal("fallback miss allocated or returned a value")
	}
}

func indexedGCFixture() *IndexedPointerLinkStore[indexedTestKey, indexedTestValue] {
	store := new(IndexedPointerLinkStore[indexedTestKey, indexedTestValue])
	for i := 1; i <= 2048; i++ {
		key := &indexedTestKey{n: i, tail: new([64]int)}
		key.tail[63] = i
		value := store.Get(key, uint32(i))
		value.n = i
		value.tail = new([64]int)
		value.tail[63] = i * 3
	}
	return store
}

func TestIndexedPointerLinksTypedRootsAndDisplacedValues(t *testing.T) {
	store := indexedGCFixture()
	entry := store.entry(1)
	old := entry.value
	fresh := store.New(entry.key, 1)
	fresh.n = 4000
	for range 3 {
		runtime.GC()
	}
	if old.n != 1 || old.tail[63] != 3 || store.entry(1).value != fresh {
		t.Fatal("displaced value lost its typed allocation")
	}
	for i := 1; i <= 2048; i++ {
		e := store.entry(uint32(i))
		if e.key.n != i || e.key.tail[63] != i {
			t.Fatalf("key graph lost at %d", i)
		}
		if i > 1 && (e.value.n != i || e.value.tail[63] != i*3) {
			t.Fatalf("value graph lost at %d", i)
		}
	}
	runtime.KeepAlive(store)
	runtime.KeepAlive(old)
}
