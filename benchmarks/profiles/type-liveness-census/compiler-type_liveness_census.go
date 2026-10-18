package compiler

import (
	"encoding/json"
	"fmt"
	"os"
	"runtime"

	"github.com/microsoft/typescript-go/internal/checker"
)

// WriteTypeLivenessCensus is diagnostic-only and runs after normal CLI checking.
// It neither constructs checkers nor forces semantic queries. Both GC cycles
// and serialization are outside the normal work and are not benchmark evidence.
func (p *Program) WriteTypeLivenessCensus() error {
	path := os.Getenv("TSC_GO_TYPE_LIVENESS_CENSUS")
	if path == "" {
		return nil
	}
	if p.opts.Tracing != nil {
		return fmt.Errorf("type liveness census requires tracing disabled")
	}
	pool := p.compilerCheckerPool
	if pool == nil {
		return fmt.Errorf("type liveness census requires built-in checker pool")
	}
	for _, mu := range pool.locks {
		if mu != nil {
			mu.Lock()
		}
	}
	defer func() {
		for i := len(pool.locks) - 1; i >= 0; i-- {
			if pool.locks[i] != nil {
				pool.locks[i].Unlock()
			}
		}
	}()
	runtime.GC()
	runtime.GC()
	report := struct {
		SchemaVersion int
		ForcedGCs     int
		Scope         string
		Owners        []checker.TypeLivenessSnapshot
	}{SchemaVersion: 1, ForcedGCs: 2, Scope: "Deterministic bounded sample of constructions at ordinals 1,65,...; checkers/program kept alive across forced GC. Cleared weak references demonstrate reclamation. Available references do not prove semantic necessity. Not an unbiased population estimate, retained-byte count, timing, or speedup result."}
	for _, c := range pool.checkers {
		if c == nil {
			continue
		}
		snapshot, ok := c.TypeLivenessSnapshot()
		if !ok {
			return fmt.Errorf("type liveness observer was not enabled at checker construction")
		}
		if snapshot.IdentityMismatches != 0 {
			return fmt.Errorf("type liveness identity mismatch")
		}
		report.Owners = append(report.Owners, snapshot)
	}
	runtime.KeepAlive(p)
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(data, '\n'), 0644)
}
