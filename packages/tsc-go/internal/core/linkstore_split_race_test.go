package core

import (
	"sync"
	"testing"
)

func TestLinkStoreConcurrentExistingKeyReads(t *testing.T) {
	var store LinkStore[int, linkStoreTestValue]
	const count = 64
	entries := make([]*linkStoreTestValue, count)
	for key := range count {
		if key%2 == 0 {
			entries[key] = store.Get(key)
		} else {
			entries[key] = store.New(key)
		}
		entries[key].count = key + 1
	}
	// Copies are only read after population. Copying an arena-backed store and
	// then inserting independently is not supported by its existing allocator.
	copyForReads := store
	var workers sync.WaitGroup
	for worker := range 8 {
		workers.Go(func() {
			current := &store
			if worker%2 != 0 {
				current = &copyForReads
			}
			for iteration := range 128 {
				// Interleave the most recently inserted entry with older entries. A read-through
				// cache that writes on a hit would race here under go test -race.
				key := (iteration + worker) % count
				if iteration%2 == 0 {
					key = count - 1
				}
				if current.Get(key) != entries[key] || current.TryGet(key) != entries[key] || !current.Has(key) || current.Get(key).count != key+1 {
					t.Errorf("reader %d lost key %d", worker, key)
					return
				}
				if current.Has(count) || current.TryGet(count) != nil {
					t.Errorf("reader %d found an absent entry", worker)
					return
				}
			}
		})
	}
	workers.Wait()
}
