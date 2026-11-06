package checker

import "github.com/microsoft/typescript-go/internal/ast"

// The table still owns both typed pointers. Escaping either member also retains
// its sibling and slab; this deliberately changes retention, not logical identity.
type instantiatedSymbolRecord struct {
	symbol ast.Symbol
	links  ValueSymbolLinks
}

func (c *Checker) newInstantiatedSymbolRecord(flags ast.SymbolFlags, name string) (*ast.Symbol, *ValueSymbolLinks) {
	c.SymbolCount++
	record := c.instantiatedSymbolArena.New()
	record.symbol.Flags = flags | ast.SymbolFlagsTransient
	record.symbol.Name = name
	return &record.symbol, &record.links
}
