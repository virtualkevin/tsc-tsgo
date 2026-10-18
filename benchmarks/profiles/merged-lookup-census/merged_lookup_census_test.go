package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func TestMergedLookupCensusPreservesLookupAndReplacement(t *testing.T) {
	s := &mergedLookupCensus{}
	c := &Checker{mergedSymbols: make(map[*ast.Symbol]*ast.Symbol), mergedLookupCensus: s}
	source, first, second := &ast.Symbol{}, &ast.Symbol{}, &ast.Symbol{}
	if c.getMergedSymbol(nil) != nil || s.Lookups != 0 {
		t.Fatal("nil input must bypass lookup")
	}
	if c.getMergedSymbol(source) != source {
		t.Fatal("absent symbol changed")
	}
	c.recordMergedSymbol(first, source)
	if c.getMergedSymbol(source) != first {
		t.Fatal("first replacement missing")
	}
	c.recordMergedSymbol(second, source)
	if c.getMergedSymbol(source) != second {
		t.Fatal("replacement update missing")
	}
	c.recordMergedSymbol(nil, source)
	if c.getMergedSymbol(source) != source {
		t.Fatal("nil replacement must return original")
	}
	if s.Lookups != 4 || s.Replacements != 2 || s.Unchanged != 2 || s.Writes != 3 || s.PeakKeys != 1 {
		t.Fatalf("unexpected counters: %+v", s)
	}
	if s.LookupSizeBuckets[0] != 1 || s.LookupSizeBuckets[1] != 3 || s.UnchangedSizeBuckets[0] != 1 || s.UnchangedSizeBuckets[1] != 1 {
		t.Fatal("size bucket mismatch")
	}
}

func TestMergedLookupCensusBucketsAndOwners(t *testing.T) {
	a, b := &mergedLookupCensus{}, &mergedLookupCensus{}
	for _, size := range []int{0, 1, 2, 3, 4, 7, 8} {
		a.lookup(size, false)
	}
	expected := []uint64{1, 1, 2, 2, 1}
	for i, n := range expected {
		if a.LookupSizeBuckets[i] != n || a.UnchangedSizeBuckets[i] != n {
			t.Fatalf("bucket %d", i)
		}
	}
	if b.Lookups != 0 {
		t.Fatal("owners shared counters")
	}
}

func TestMergedLookupCensusDisabledKeepsSemantics(t *testing.T) {
	c := &Checker{mergedSymbols: make(map[*ast.Symbol]*ast.Symbol)}
	source, target := &ast.Symbol{}, &ast.Symbol{}
	if c.getMergedSymbol(source) != source {
		t.Fatal("absent result")
	}
	c.recordMergedSymbol(target, source)
	if c.getMergedSymbol(source) != target {
		t.Fatal("replacement result")
	}
}
