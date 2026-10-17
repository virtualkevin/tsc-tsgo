package ast

import (
	"runtime"
	"testing"
)

func TestIndexedSymbolLinksAllocationDomains(t *testing.T) {
	type value struct {
		target *Symbol
		text   string
	}
	var allocator SymbolAllocator
	allocated := allocator.New()
	unindexed := &Symbol{Name: "external"}
	copiedHandle := &Symbol{Name: "same handle, distinct identity", linkIndex: allocated.linkIndex}
	var first, second IndexedSymbolLinks[value]
	keys := []*Symbol{allocated, unindexed, copiedHandle, nil}
	for _, key := range keys {
		if first.Has(key) || first.TryGet(key) != nil {
			t.Fatal("miss populated links")
		}
		a, b := first.Get(key), second.Get(key)
		if a == b {
			t.Fatal("checker-local stores share values")
		}
		a.target, a.text = key, "first"
		b.target, b.text = key, "second"
	}
	old := first.Get(allocated)
	replacement := first.New(allocated)
	if old == replacement || *replacement != (value{}) {
		t.Fatal("New failed to replace with zero value")
	}
	replacement.target, replacement.text = allocated, "replacement"
	allocator = SymbolAllocator{} // Model binder reset: abandon, never recycle.
	afterReset := allocator.New()
	if afterReset.linkIndex == allocated.linkIndex || afterReset.linkIndex == 0 {
		t.Fatal("reset recycled a handle")
	}
	for range 3 {
		runtime.GC()
	}
	for _, key := range keys {
		a, b := first.TryGet(key), second.TryGet(key)
		want := "first"
		if key == allocated {
			want = "replacement"
		}
		if a == nil || b == nil || a.text != want || b.text != "second" || a.target != key || b.target != key {
			t.Fatal("domain identity or retained value changed")
		}
	}
	if old.text != "first" || old.target != allocated {
		t.Fatal("displaced pointer lost value")
	}
	if allocated.id.Load() != 0 || unindexed.id.Load() != 0 || copiedHandle.id.Load() != 0 || afterReset.id.Load() != 0 {
		t.Fatal("links access forced semantic IDs")
	}
	runtime.KeepAlive(first)
	runtime.KeepAlive(second)
	runtime.KeepAlive(old)
}
