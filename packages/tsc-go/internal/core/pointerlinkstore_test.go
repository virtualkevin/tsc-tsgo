package core

import (
	"math/rand/v2"
	"runtime"
	"sync"
	"testing"
)

type pointerLinkKey struct {
	padding [3]uint64
	tail    int
}

type pointerLinkValue struct {
	count int
	ref   *int
}

func TestPointerLinkStoreDifferential(t *testing.T) {
	var got PointerLinkStore[pointerLinkKey, pointerLinkValue]
	var want LinkStore[*pointerLinkKey, pointerLinkValue]
	keys := make([]*pointerLinkKey, 1025)
	for i := 1; i < len(keys); i++ {
		keys[i] = &pointerLinkKey{tail: i}
	}
	gotPointers := make(map[*pointerLinkKey]*pointerLinkValue)
	wantPointers := make(map[*pointerLinkKey]*pointerLinkValue)
	rng := rand.New(rand.NewPCG(17, 91))
	for step := range 20000 {
		key := keys[rng.IntN(len(keys))]
		switch rng.IntN(4) {
		case 0, 1:
			var a, b *pointerLinkValue
			fresh := step%3 == 0
			if fresh {
				a, b = got.New(key), want.New(key)
			} else {
				a, b = got.Get(key), want.Get(key)
			}
			if fresh || gotPointers[key] == nil {
				if *a != (pointerLinkValue{}) || *b != (pointerLinkValue{}) {
					t.Fatal("new entry was not zero initialized")
				}
			} else if a != gotPointers[key] || b != wantPointers[key] {
				t.Fatal("Get changed existing pointer identity")
			}
			a.count, b.count = step+1, step+1
			gotPointers[key], wantPointers[key] = a, b
		case 2:
			if got.Has(key) != want.Has(key) {
				t.Fatal("membership mismatch")
			}
		case 3:
			a, b := got.TryGet(key), want.TryGet(key)
			if (a == nil) != (b == nil) || a != nil && a.count != b.count {
				t.Fatal("lookup mismatch")
			}
		}
	}
	if got.count != len(gotPointers) {
		t.Fatal("replacement changed the number of keys")
	}
	for key, entry := range gotPointers {
		if got.Get(key) != entry || got.TryGet(key).count != want.TryGet(key).count {
			t.Fatal("growth or replacement lost an entry")
		}
	}
}

func TestPointerLinkStoreNilAndReplacement(t *testing.T) {
	var store PointerLinkStore[pointerLinkKey, pointerLinkValue]
	if store.Has(nil) || store.TryGet(nil) != nil || store.entries != nil {
		t.Fatal("empty reads allocated or found nil")
	}
	first := store.New(nil)
	first.count = 19
	if store.Get(nil) != first || !store.Has(nil) {
		t.Fatal("nil key was not preserved")
	}
	second := store.New(nil)
	if first == second || *second != (pointerLinkValue{}) || first.count != 19 || store.count != 1 {
		t.Fatal("duplicate New did not replace with fresh storage")
	}
}

func TestPointerLinkStoreCollisionsAndGrowth(t *testing.T) {
	var store PointerLinkStore[pointerLinkKey, pointerLinkValue]
	// Arena-like contiguous addresses with fixed stride. At least one bucket
	// contains 16 keys by pigeonhole; no allocator-address assumption is used.
	keys := make([]pointerLinkKey, 256)
	var buckets [16][]*pointerLinkKey
	for i := range keys {
		bucket := pointerLinkHash(&keys[i]) & 15
		buckets[bucket] = append(buckets[bucket], &keys[i])
	}
	var collision []*pointerLinkKey
	for _, bucket := range buckets {
		if len(bucket) >= 16 {
			collision = bucket
			break
		}
	}
	entries := make([]*pointerLinkValue, len(collision))
	for i, key := range collision {
		entries[i] = store.New(key)
		entries[i].count = i + 1
		if i == 11 && len(store.entries) != 16 {
			t.Fatal("table grew before reaching its load boundary")
		}
		if i == 12 && len(store.entries) != 32 {
			t.Fatal("table did not grow at its load boundary")
		}
	}
	for i, key := range collision {
		if store.TryGet(key) != entries[i] || store.Get(key).count != i+1 {
			t.Fatal("collision chain lost a value during growth")
		}
	}
	// Explicit wraparound is independently tested without requiring addresses
	// to land in any particular allocator-selected bucket.
	var wrapped PointerLinkStore[pointerLinkKey, pointerLinkValue]
	wrapped.entries = make([]pointerLinkEntry[pointerLinkKey, pointerLinkValue], 16)
	missing := &pointerLinkKey{}
	start := int(pointerLinkHash(missing) & 15)
	occupied := &pointerLinkKey{tail: 1}
	value := &pointerLinkValue{count: 1}
	for offset := range 15 {
		wrapped.entries[(start+offset)&15] = pointerLinkEntry[pointerLinkKey, pointerLinkValue]{occupied, value}
	}
	if wrapped.slot(missing) != (start+15)&15 || wrapped.Has(missing) {
		t.Fatal("probe did not wrap to the empty slot")
	}
}

//go:noinline
func pointerLinkPopulateForGC() PointerLinkStore[pointerLinkKey, pointerLinkValue] {
	var store PointerLinkStore[pointerLinkKey, pointerLinkValue]
	var keys Arena[pointerLinkKey]
	for i := range 4096 {
		key := keys.New()
		key.tail = i + 1
		value := store.New(key)
		value.count = i + 1
		value.ref = new(int)
		*value.ref = i + 1
	}
	// Both arenas' old chunks are reachable only through retained interior
	// pointers. Returning a store copy also exercises read-only copying.
	return store
}

func TestPointerLinkStoreRetainsDisplacedArenaSlots(t *testing.T) {
	store := pointerLinkPopulateForGC()
	runtime.GC()
	runtime.GC()
	seen := 0
	for _, entry := range store.entries {
		if entry.value == nil {
			continue
		}
		seen++
		if entry.key.tail != entry.value.count || *entry.value.ref != entry.value.count || store.TryGet(entry.key) != entry.value {
			t.Fatal("typed key/value reachability or identity was lost")
		}
	}
	if seen != 4096 {
		t.Fatalf("only %d retained entries", seen)
	}
}

func TestPointerLinkStoreConcurrentReadOnlyCopies(t *testing.T) {
	store := pointerLinkPopulateForGC()
	copyForReads := store
	keys := make([]*pointerLinkKey, 0, store.count)
	for _, entry := range store.entries {
		if entry.value != nil {
			keys = append(keys, entry.key)
		}
	}
	missing := &pointerLinkKey{}
	var workers sync.WaitGroup
	for worker := range 8 {
		workers.Go(func() {
			current := &store
			if worker%2 == 0 {
				current = &copyForReads
			}
			for i := range 1024 {
				key := keys[(i*17+worker)%len(keys)]
				value := current.Get(key)
				if value != current.TryGet(key) || !current.Has(key) || value.count != key.tail || current.Has(missing) || current.TryGet(missing) != nil {
					t.Error("read-only lookup changed identity or membership")
					return
				}
			}
		})
	}
	workers.Wait()
}
