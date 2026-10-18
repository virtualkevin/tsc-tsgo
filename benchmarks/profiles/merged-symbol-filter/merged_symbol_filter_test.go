package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"runtime"
	"testing"
)

func TestMergedSymbolFilterPreservesUpdatesAndOwners(t *testing.T) {
	a := &Checker{mergedSymbols: make(map[*ast.Symbol]*ast.Symbol)}
	b := &Checker{mergedSymbols: make(map[*ast.Symbol]*ast.Symbol)}
	source, first, last := &ast.Symbol{}, &ast.Symbol{}, &ast.Symbol{}
	if a.getMergedSymbol(nil) != nil || a.getMergedSymbol(source) != source {
		t.Fatal("empty lookup")
	}
	a.recordMergedSymbol(first, source)
	if a.getMergedSymbol(source) != first || b.getMergedSymbol(source) != source {
		t.Fatal("replacement or checker isolation")
	}
	a.recordMergedSymbol(last, source)
	if a.getMergedSymbol(source) != last {
		t.Fatal("updated replacement")
	}
	a.recordMergedSymbol(nil, source)
	if a.getMergedSymbol(source) != source {
		t.Fatal("nil-valued replacement")
	}
}

func TestMergedSymbolFilterMapGrowthAndGC(t *testing.T) {
	c := &Checker{mergedSymbols: make(map[*ast.Symbol]*ast.Symbol)}
	sources := make([]ast.Symbol, 20000)
	targets := make([]ast.Symbol, len(sources))
	for i := range sources {
		c.recordMergedSymbol(&targets[i], &sources[i])
	}
	runtime.GC()
	for i := range sources {
		if c.getMergedSymbol(&sources[i]) != &targets[i] {
			t.Fatalf("lost replacement %d", i)
		}
	}
	absent := make([]ast.Symbol, 20000)
	for i := range absent {
		if c.getMergedSymbol(&absent[i]) != &absent[i] {
			t.Fatal("filter false positive changed semantics")
		}
	}
}
