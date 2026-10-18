package ast

import (
	"runtime"
	"sync"
	"testing"
	"unsafe"
)

type ownedLinksTestValue struct {
	next *Symbol
	text string
}

func TestOwnedSymbolLinksIsolationAndReplacement(t *testing.T) {
	var a, b OwnedSymbolLinks[ownedLinksTestValue]
	owned := a.NewSymbol()
	if len(a.ownedKeys) != 0 {
		t.Fatal("unlinked key retained")
	}
	if a.Has(owned) || a.TryGet(owned) != nil || b.Has(owned) {
		t.Fatal("allocation created links")
	}
	first := a.Get(owned)
	first.text = "first"
	first.next = &Symbol{Name: "retained"}
	if a.Get(owned) != first || a.fallback.Has(owned) {
		t.Fatal("owned lookup used fallback or changed identity")
	}
	foreign := b.Get(owned)
	foreign.text = "foreign"
	if foreign == first || a.Get(owned).text != "first" {
		t.Fatal("cross-owner alias")
	}
	replacement := a.New(owned)
	if replacement == first || *replacement != (ownedLinksTestValue{}) || first.text != "first" {
		t.Fatal("replacement lifetime")
	}
	// Copy only the immutable metadata, without copying Symbol's atomic member.
	// A distinct symbol carrying copied metadata must take the pointer fallback.
	copied := &Symbol{ownedLinks: owned.ownedLinks}
	if a.Has(copied) {
		t.Fatal("copied metadata aliases original")
	}
	a.Get(copied).text = "copy"
	if !a.fallback.Has(copied) || a.Get(owned) != replacement {
		t.Fatal("copy fallback")
	}
	for _, key := range []*Symbol{nil, {}, owned, copied} {
		old := a.Get(key)
		old.text = "old"
		fresh := a.New(key)
		if fresh == old || fresh.text != "" || old.text != "old" {
			t.Fatal("new contract")
		}
	}
	if len(a.ownedKeys) != 1 || a.ownedKeys[0] != owned {
		t.Fatal("owned roots missing or duplicated")
	}
	runtime.GC()
	if first.next.Name != "retained" || foreign.text != "foreign" {
		t.Fatal("typed roots lost")
	}
	runtime.KeepAlive(a)
	runtime.KeepAlive(b)
	t.Logf("symbol=%d owned record=%d metadata=%d", unsafe.Sizeof(Symbol{}), unsafe.Sizeof(ownedSymbol[ownedLinksTestValue]{}), unsafe.Sizeof(ownedSymbolData[ownedLinksTestValue]{}))
}

func TestOwnedSymbolLinksGrowthAndConcurrentReads(t *testing.T) {
	var s OwnedSymbolLinks[ownedLinksTestValue]
	keys := make([]*Symbol, 4096)
	values := make([]*ownedLinksTestValue, len(keys))
	for i := range keys {
		keys[i] = s.NewSymbol()
		values[i] = s.Get(keys[i])
		values[i].next = keys[i]
	}
	runtime.GC()
	var wg sync.WaitGroup
	for range 8 {
		wg.Go(func() {
			for i, key := range keys {
				if s.Get(key) != values[i] || s.TryGet(key).next != key || !s.Has(key) {
					t.Error("unstable value")
				}
			}
		})
	}
	wg.Wait()
	runtime.KeepAlive(s)
}

func TestOwnedSymbolLinksForeignReadDuringOwnerWrites(t *testing.T) {
	var owner, foreign OwnedSymbolLinks[ownedLinksTestValue]
	key := owner.NewSymbol()
	foreign.Get(key).text = "foreign"
	var wg sync.WaitGroup
	wg.Go(func() {
		for range 10000 {
			owner.New(key).text = "owner"
		}
	})
	wg.Go(func() {
		for range 10000 {
			if foreign.Get(key).text != "foreign" {
				t.Error("foreign changed")
			}
		}
	})
	wg.Wait()
}
