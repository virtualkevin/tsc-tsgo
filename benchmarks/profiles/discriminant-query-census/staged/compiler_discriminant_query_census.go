package compiler

import (
	"fmt"
	"os"

	"github.com/microsoft/typescript-go/internal/checker"
)

// WriteDiscriminantQueryCensus is diagnostic-only and runs after normal CLI checking.
// It neither constructs checkers nor forces semantic queries or GC.
func (p *Program) WriteDiscriminantQueryCensus() error {
	path := os.Getenv("TSC_GO_DISCRIMINANT_QUERY_CENSUS")
	if path == "" {
		return nil
	}
	if p.opts.Tracing != nil {
		return fmt.Errorf("discriminant query census requires tracing disabled")
	}
	pool := p.compilerCheckerPool
	if pool == nil {
		return fmt.Errorf("discriminant query census requires built-in checker pool")
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
	owners := []checker.DiscriminantQuerySnapshot{}
	for _, c := range pool.checkers {
		if c == nil {
			continue
		}
		snapshot, ok := c.DiscriminantQuerySnapshot()
		if !ok {
			return fmt.Errorf("discriminant query observer not enabled at construction")
		}
		owners = append(owners, snapshot)
	}
	return checker.WriteDiscriminantQuerySnapshots(path, owners)
}
