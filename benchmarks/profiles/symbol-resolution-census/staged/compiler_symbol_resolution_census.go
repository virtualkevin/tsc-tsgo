package compiler

import (
	"fmt"
	"os"

	"github.com/microsoft/typescript-go/internal/checker"
)

// WriteSymbolResolutionCensus is diagnostic-only and runs after normal CLI checking.
// It neither constructs checkers nor forces semantic queries or GC.
func (p *Program) WriteSymbolResolutionCensus() error {
	path := os.Getenv("TSC_GO_SYMBOL_RESOLUTION_CENSUS")
	if path == "" {
		return nil
	}
	if p.opts.Tracing != nil {
		return fmt.Errorf("symbol resolution census requires tracing disabled")
	}
	pool := p.compilerCheckerPool
	if pool == nil {
		return fmt.Errorf("symbol resolution census requires built-in checker pool")
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
	owners := []checker.SymbolResolutionSnapshot{}
	for _, c := range pool.checkers {
		if c == nil {
			continue
		}
		snapshot, ok := c.SymbolResolutionSnapshot()
		if !ok {
			return fmt.Errorf("symbol resolution observer not enabled at construction")
		}
		owners = append(owners, snapshot)
	}
	return checker.WriteSymbolResolutionSnapshots(path, owners)
}
