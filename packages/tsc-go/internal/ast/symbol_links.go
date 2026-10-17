package ast

import "github.com/microsoft/typescript-go/internal/core"

// IndexedSymbolLinks retains checker-local values. Symbols supply only immutable
// allocation handles; no checker-owned state is published on shared symbols.
type IndexedSymbolLinks[V any] struct {
	store core.IndexedPointerLinkStore[Symbol, V]
}

func symbolLinkIndex(symbol *Symbol) uint32 {
	if symbol == nil {
		return 0
	}
	return symbol.linkIndex
}
func (s *IndexedSymbolLinks[V]) Get(symbol *Symbol) *V {
	return s.store.Get(symbol, symbolLinkIndex(symbol))
}
func (s *IndexedSymbolLinks[V]) New(symbol *Symbol) *V {
	return s.store.New(symbol, symbolLinkIndex(symbol))
}
func (s *IndexedSymbolLinks[V]) TryGet(symbol *Symbol) *V {
	return s.store.TryGet(symbol, symbolLinkIndex(symbol))
}
func (s *IndexedSymbolLinks[V]) Has(symbol *Symbol) bool {
	return s.store.Has(symbol, symbolLinkIndex(symbol))
}
