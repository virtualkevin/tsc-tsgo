package ast

import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"
	"sync"
	"weak"
)

// Diagnostic observer only. Sampling does not keep symbols or their graphs alive.
// Ordinals are per origin, so concurrent scheduling affects sample membership.
type symbolColdGroup struct {
	Constructed uint64
	Eligible    uint64
	Overflow    uint64
	Samples     []weak.Pointer[Symbol] `json:"-"`
}
type symbolColdCensus struct {
	mu     sync.Mutex
	groups [2]symbolColdGroup
	stride uint64
	limit  int
}
type symbolColdReport struct {
	Constructed uint64
	Eligible    uint64
	Overflow    uint64
	Sampled     int
	Cleared     uint64
	// Bit 0: Members != nil; bit 1: Exports != nil; bit 2: ExportSymbol != nil.
	LiveMasks [8]uint64
}

var symbolColdOutput = os.Getenv("TSC_GO_SYMBOL_COLD_CENSUS")
var symbolColdObserver = symbolColdCensus{stride: 64, limit: 262144}

func ObserveSymbolColdFields(symbol *Symbol, origin int) {
	if symbolColdOutput != "" {
		symbolColdObserver.observe(symbol, origin)
	}
}

func (o *symbolColdCensus) observe(symbol *Symbol, origin int) {
	o.mu.Lock()
	defer o.mu.Unlock()
	g := &o.groups[origin]
	g.Constructed++
	if (g.Constructed-1)%o.stride != 0 {
		return
	}
	g.Eligible++
	if len(g.Samples) == o.limit {
		g.Overflow++
		return
	}
	g.Samples = append(g.Samples, weak.Make(symbol))
}

// Call only after ordinary compiler work is complete. The mutex protects the
// observer ledger, not concurrent writes to Symbol fields by compiler clients.
func (o *symbolColdCensus) snapshot() [2]symbolColdReport {
	o.mu.Lock()
	defer o.mu.Unlock()
	var result [2]symbolColdReport
	for i, g := range o.groups {
		r := &result[i]
		r.Constructed, r.Eligible, r.Overflow = g.Constructed, g.Eligible, g.Overflow
		r.Sampled = len(g.Samples)
		for _, sample := range g.Samples {
			s := sample.Value()
			if s == nil {
				r.Cleared++
				continue
			}
			mask := 0
			if s.Members != nil {
				mask |= 1
			}
			if s.Exports != nil {
				mask |= 2
			}
			if s.ExportSymbol != nil {
				mask |= 4
			}
			r.LiveMasks[mask]++
			runtime.KeepAlive(s)
		}
	}
	return result
}

func WriteSymbolColdFields(owner any, tracing bool) error {
	if symbolColdOutput == "" {
		return nil
	}
	if tracing {
		return fmt.Errorf("symbol cold census cannot run with tracing")
	}
	defer runtime.KeepAlive(owner)
	runtime.GC()
	runtime.GC()
	report := struct {
		SchemaVersion int
		Stride        uint64
		Limit         int
		Origins       [2]string
		Groups        [2]symbolColdReport
	}{1, symbolColdObserver.stride, symbolColdObserver.limit, [2]string{"binder", "checker"}, symbolColdObserver.snapshot()}
	f, err := os.OpenFile(symbolColdOutput, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
