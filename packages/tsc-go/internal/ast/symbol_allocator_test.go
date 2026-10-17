package ast

import (
	"sync"
	"sync/atomic"
	"testing"
)

func TestSymbolAllocationHandlesPreserveLazySemanticIDs(t *testing.T) {
	var allocator SymbolAllocator
	first, second := allocator.New(), allocator.New()
	if first.linkIndex == 0 || second.linkIndex == 0 || first.linkIndex == second.linkIndex {
		t.Fatal("allocation handles missing or repeated")
	}
	if first.id.Load() != 0 || second.id.Load() != 0 {
		t.Fatal("allocation forced a semantic ID")
	}
	secondID, firstID := GetSymbolId(second), GetSymbolId(first)
	if secondID >= firstID {
		t.Fatal("semantic IDs no longer follow their first query order")
	}
	if (&Symbol{}).linkIndex != 0 {
		t.Fatal("foreign symbol unexpectedly indexed")
	}
}

func TestSymbolAllocationHandleExhaustionDoesNotWrap(t *testing.T) {
	var counter atomic.Uint32
	counter.Store(maxSymbolLinkBlock - 1)
	var cursor symbolLinkCursor
	for i := uint32(0); i < symbolLinkBlockSize; i++ {
		got := cursor.take(&counter)
		want := maxSymbolLinkBlock<<symbolLinkBlockShift | i
		if got != want || got == 0 {
			t.Fatalf("handle %d: got %x want %x", i, got, want)
		}
	}
	for range 3 {
		if cursor.take(&counter) != 0 {
			t.Fatal("exhausted allocator reused a handle")
		}
	}
	var other symbolLinkCursor
	if other.take(&counter) != 0 || counter.Load() != maxSymbolLinkBlock {
		t.Fatal("global exhaustion was not permanent")
	}
}

func TestSymbolAllocationHandleConcurrentOwners(t *testing.T) {
	var counter atomic.Uint32
	const owners, perOwner = 8, 3*symbolLinkBlockSize + 17
	results := make(chan []uint32, owners)
	var workers sync.WaitGroup
	for range owners {
		workers.Go(func() {
			var cursor symbolLinkCursor
			ids := make([]uint32, perOwner)
			for i := range ids {
				ids[i] = cursor.take(&counter)
			}
			results <- ids
		})
	}
	workers.Wait()
	close(results)
	seen := make(map[uint32]bool)
	for ids := range results {
		for _, id := range ids {
			if id == 0 || seen[id] {
				t.Fatalf("reused handle %x", id)
			}
			seen[id] = true
		}
	}
	if len(seen) != owners*perOwner || counter.Load() != owners*4 {
		t.Fatal("block reservation count differs")
	}
}
