package core

import "testing"

type linkStoreTestValue struct {
	count int
	ref   *int
}

func TestLinkStoreNewPreservesIdentityAndValues(t *testing.T) {
	var store LinkStore[*int, linkStoreTestValue]
	firstKey, secondKey := new(int), new(int)
	if store.Has(firstKey) || store.TryGet(firstKey) != nil {
		t.Fatal("absent key already has links")
	}
	first := store.New(firstKey)
	if *first != (linkStoreTestValue{}) {
		t.Fatalf("new links are not zero-valued: %+v", *first)
	}
	first.count = 42
	first.ref = secondKey
	second := store.New(secondKey)
	second.count = 17
	if first == second {
		t.Fatal("distinct pointer keys share a link entry")
	}
	for _, key := range []*int{firstKey, secondKey} {
		if !store.Has(key) {
			t.Fatal("New did not add the key")
		}
		if store.Get(key) != store.TryGet(key) {
			t.Fatal("Get and TryGet return different link entries")
		}
	}
	if store.Get(firstKey) != first || first.count != 42 || first.ref != secondKey {
		t.Fatal("subsequent lookup changed the first entry's identity or value")
	}
	if store.Get(secondKey) != second || second.count != 17 {
		t.Fatal("subsequent lookup changed the second entry's identity or value")
	}
}

func TestLinkStoreNewAndGetPreserveEntriesAcrossGrowth(t *testing.T) {
	var store LinkStore[int, linkStoreTestValue]
	const count = 2048 // Cross several arena and map growth boundaries.
	entries := make([]*linkStoreTestValue, count)
	values := make([]int, count)
	for key := range count {
		if key%2 == 0 {
			entries[key] = store.New(key)
		} else {
			entries[key] = store.Get(key)
		}
		if *entries[key] != (linkStoreTestValue{}) {
			t.Fatalf("key %d did not receive zero-valued links", key)
		}
		entries[key].count = key + 1
		entries[key].ref = &values[key]
	}
	for key, want := range entries {
		got := store.Get(key)
		if got != want || got.count != key+1 || got.ref != &values[key] {
			t.Fatalf("key %d lost its entry or value during growth", key)
		}
		*got.ref = key + 7
		if values[key] != key+7 {
			t.Fatalf("key %d lost its referenced value", key)
		}
	}
}

func TestLinkStoreNewAcceptsNilPointerKey(t *testing.T) {
	var store LinkStore[*int, linkStoreTestValue]
	entry := store.New(nil)
	entry.count = 7
	if !store.Has(nil) || store.TryGet(nil) != entry || store.Get(nil) != entry || entry.count != 7 {
		t.Fatal("nil key did not retain its entry")
	}
}
