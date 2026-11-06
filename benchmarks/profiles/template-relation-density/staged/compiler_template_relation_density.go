package compiler

import (
	"fmt"
	"os"

	"github.com/microsoft/typescript-go/internal/checker"
)

// WriteTemplateRelationDensity is diagnostic-only and runs after normal CLI checking.
// It neither constructs checkers nor forces semantic queries or GC.
func (p *Program) WriteTemplateRelationDensity() error {
	path := os.Getenv("TSC_GO_TEMPLATE_RELATION_DENSITY")
	if path == "" {
		return nil
	}
	if p.opts.Tracing != nil {
		return fmt.Errorf("template relation density census requires tracing disabled")
	}
	pool := p.compilerCheckerPool
	if pool == nil {
		return fmt.Errorf("template relation density census requires built-in checker pool")
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
	owners := []checker.TemplateRelationDensitySnapshot{}
	for _, c := range pool.checkers {
		if c == nil {
			continue
		}
		snapshot, ok := c.TemplateRelationDensitySnapshot()
		if !ok {
			return fmt.Errorf("template relation density observer not enabled at construction")
		}
		owners = append(owners, snapshot)
	}
	return checker.WriteTemplateRelationDensitySnapshots(path, owners)
}
