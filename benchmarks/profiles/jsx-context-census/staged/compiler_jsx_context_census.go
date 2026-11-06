package compiler

import (
	"fmt"
	"os"

	"github.com/microsoft/typescript-go/internal/checker"
)

// WriteJsxContextCensus is diagnostic-only and runs after normal CLI checking.
// It neither constructs checkers nor forces semantic queries or GC.
func (p *Program) WriteJsxContextCensus() error {
	path := os.Getenv("TSC_GO_JSX_CONTEXT_CENSUS")
	if path == "" {
		return nil
	}
	if p.opts.Tracing != nil {
		return fmt.Errorf("jsx context census requires tracing disabled")
	}
	pool := p.compilerCheckerPool
	if pool == nil {
		return fmt.Errorf("jsx context census requires built-in checker pool")
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
	owners := []checker.JsxContextSnapshot{}
	for _, c := range pool.checkers {
		if c == nil {
			continue
		}
		snapshot, ok := c.JsxContextSnapshot()
		if !ok {
			return fmt.Errorf("jsx context observer not enabled at construction")
		}
		owners = append(owners, snapshot)
	}
	return checker.WriteJsxContextSnapshots(path, owners)
}
