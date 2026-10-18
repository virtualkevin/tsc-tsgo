package compiler

import (
	"fmt"
	"os"

	"github.com/microsoft/typescript-go/internal/checker"
)

// WriteSymbolRequestCensus is diagnostic-only and runs after normal CLI checking.
// It neither constructs checkers nor forces semantic queries or GC.
func (p *Program) WriteSymbolRequestCensus() error {
	path := os.Getenv("TSC_GO_SYMBOL_REQUEST_CENSUS")
	if path == "" {
		return nil
	}
	if p.opts.Tracing != nil {
		return fmt.Errorf("symbol request census requires tracing disabled")
	}
	pool := p.compilerCheckerPool
	if pool == nil {
		return fmt.Errorf("symbol request census requires built-in checker pool")
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
	owners := []checker.SymbolRequestSnapshot{}
	for _, c := range pool.checkers {
		if c == nil {
			continue
		}
		snapshot, ok := c.SymbolRequestSnapshot()
		if !ok {
			return fmt.Errorf("symbol request observer not enabled at construction")
		}
		owners = append(owners, snapshot)
	}
	return checker.WriteSymbolRequestSnapshots(path, owners)
}
