package checker

import (
	"math/rand/v2"
	"runtime"
	"sync"
	"testing"
	"weak"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/core"
)

func TestDirectReferenceFlagsDifferential(t *testing.T) {
	c := &Checker{}
	type oldLinks struct{ kinds ast.SymbolFlags }
	var old core.LinkStore[*ast.Symbol, oldLinks]
	keys := make([]*ast.Symbol, 1025)
	for i := 1; i < len(keys); i++ {
		keys[i] = &ast.Symbol{Name: "same"}
	}
	rng := rand.New(rand.NewPCG(48, 19))
	for range 20000 {
		key := keys[rng.IntN(len(keys))]
		if rng.IntN(3) == 0 {
			kind := ast.SymbolFlags(1) << rng.IntN(32)
			c.symbolReferenced(key, kind)
			old.Get(key).kinds |= kind
		}
		if c.isReferenced(key) != (old.Get(key).kinds != 0) || c.symbolReferenceLinks[key] != old.Get(key).kinds {
			t.Fatal("reference meanings changed")
		}
	}
	for _, key := range keys {
		c.symbolReferenced(key, ast.SymbolFlagsAll)
		if c.symbolReferenceLinks[key] != old.Get(key).kinds|ast.SymbolFlagsAll {
			t.Fatal("all meaning overwrote flags")
		}
	}
}

func TestDirectReferenceFlagsReadBeforeWrite(t *testing.T) {
	a, b := &Checker{}, &Checker{}
	key := &ast.Symbol{}
	if a.isReferenced(key) || a.symbolReferenceLinks != nil {
		t.Fatal("absent read materialized state")
	}
	a.symbolReferenced(key, ast.SymbolFlagsTypeParameter)
	if !a.isReferenced(key) || b.isReferenced(key) {
		t.Fatal("checker isolation")
	}
	a.symbolReferenced(key, ast.SymbolFlagsVariable)
	if a.symbolReferenceLinks[key] != ast.SymbolFlagsTypeParameter|ast.SymbolFlagsVariable {
		t.Fatal("lost prior meaning")
	}
	a.symbolReferenced(nil, 0)
	if a.isReferenced(nil) {
		t.Fatal("zero meaning")
	}
	a.symbolReferenced(nil, ast.SymbolFlagsAll)
	if !a.isReferenced(nil) {
		t.Fatal("nil key")
	}
}

//go:noinline
func directReferenceFlagsRoot() (*Checker, weak.Pointer[ast.Symbol]) {
	c := &Checker{}
	key := &ast.Symbol{Name: "retained"}
	c.symbolReferenced(key, ast.SymbolFlagsType)
	return c, weak.Make(key)
}
func TestDirectReferenceFlagsRetainsWrittenKeys(t *testing.T) {
	c, w := directReferenceFlagsRoot()
	runtime.GC()
	runtime.GC()
	key := w.Value()
	if key == nil || !c.isReferenced(key) || key.Name != "retained" {
		t.Fatal("written key lost")
	}
	runtime.KeepAlive(c)
}

func TestDirectReferenceFlagsConcurrentReads(t *testing.T) {
	c := &Checker{}
	key := &ast.Symbol{}
	missing := &ast.Symbol{}
	c.symbolReferenced(key, ast.SymbolFlagsValue)
	var group sync.WaitGroup
	for range 8 {
		group.Go(func() {
			for range 1000 {
				if !c.isReferenced(key) || c.isReferenced(missing) {
					t.Error("read mismatch")
					return
				}
			}
		})
	}
	group.Wait()
}
