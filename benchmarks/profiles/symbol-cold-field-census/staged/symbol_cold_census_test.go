package ast

import (
	"runtime"
	"sync"
	"testing"
	"weak"
)

func TestSymbolColdCensusMasks(t *testing.T) {
	o := symbolColdCensus{stride: 1, limit: 16}
	roots := make([]*Symbol, 8)
	for mask := range roots {
		s := &Symbol{Name: "sample"}
		roots[mask] = s
		o.observe(s, 0)
		// Mutations after observation must be reflected at completion.
		if mask&1 != 0 {
			s.Members = SymbolTable{}
		}
		if mask&2 != 0 {
			s.Exports = SymbolTable{}
		}
		if mask&4 != 0 {
			s.ExportSymbol = s
		}
	}
	r := o.snapshot()[0]
	if r.Constructed != 8 || r.Eligible != 8 || r.Sampled != 8 || r.Cleared != 0 {
		t.Fatalf("counts: %+v", r)
	}
	for _, count := range r.LiveMasks {
		if count != 1 {
			t.Fatalf("masks: %v", r.LiveMasks)
		}
	}
	runtime.KeepAlive(roots)
}

func TestSymbolColdCensusSampling(t *testing.T) {
	o := symbolColdCensus{stride: 2, limit: 2}
	s := &Symbol{Name: "root"}
	for range 7 {
		o.observe(s, 1)
	}
	o.groups[1].Samples[0] = weak.Pointer[Symbol]{}
	r := o.snapshot()[1]
	if r.Constructed != 7 || r.Eligible != 4 || r.Overflow != 2 || r.Sampled != 2 || r.Cleared != 1 || r.LiveMasks[0] != 1 {
		t.Fatalf("counts: %+v", r)
	}
	if o.snapshot()[0].Constructed != 0 {
		t.Fatal("origin contamination")
	}
	runtime.KeepAlive(s)
}

func TestSymbolColdCensusConcurrentLedger(t *testing.T) {
	o := symbolColdCensus{stride: 1, limit: 512}
	s := &Symbol{Name: "shared immutable"}
	var wg sync.WaitGroup
	for origin := range 2 {
		for range 4 {
			wg.Go(func() {
				for range 64 {
					o.observe(s, origin)
				}
			})
		}
	}
	wg.Wait()
	for _, r := range o.snapshot() {
		if r.Constructed != 256 || r.Sampled != 256 || r.LiveMasks[0] != 256 {
			t.Fatalf("counts: %+v", r)
		}
	}
	runtime.KeepAlive(s)
}
