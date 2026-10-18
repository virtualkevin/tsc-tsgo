package ast

import "github.com/microsoft/typescript-go/internal/core"

// OwnedSymbolLinks avoids hashing symbols allocated by this store. Other symbols
// use the original pointer table. Mutation requires exclusive ownership; a
// completed store supports concurrent reads. Do not mutate copies of a store.
// The owner token deliberately does not point back to the store or checker.
type OwnedSymbolLinks[V any] struct {
	// Like the pointer table, retain each key once links are created. Arena
	// alone retains only its current slab. Unlinked symbols are not added.
	ownedKeys []*Symbol
	owner     *symbolLinksOwner
	symbols   core.Arena[ownedSymbol[V]]
	values    core.Arena[V]
	fallback  core.PointerLinkStore[Symbol, V]
}

type symbolLinksOwner struct{ identity byte }
type ownedSymbol[V any] struct {
	symbol Symbol
	links  ownedSymbolData[V]
}
type ownedSymbolData[V any] struct {
	owner *symbolLinksOwner
	key   *Symbol
	value *V
}

// NewSymbol publishes only immutable ownership metadata. It does not create a
// links value: Has and TryGet must still report absence until Get or New.
func (s *OwnedSymbolLinks[V]) NewSymbol() *Symbol {
	if s.owner == nil {
		s.owner = &symbolLinksOwner{}
	}
	record := s.symbols.New()
	record.links.owner = s.owner
	record.links.key = &record.symbol
	record.symbol.ownedLinks = &record.links
	return &record.symbol
}

func (s *OwnedSymbolLinks[V]) owned(key *Symbol) *ownedSymbolData[V] {
	if key != nil {
		if data, ok := key.ownedLinks.(*ownedSymbolData[V]); ok && data.owner == s.owner && data.key == key {
			return data
		}
	}
	return nil
}

func (s *OwnedSymbolLinks[V]) Get(key *Symbol) *V {
	if data := s.owned(key); data != nil {
		if data.value == nil {
			s.ownedKeys = append(s.ownedKeys, key)
			data.value = s.values.New()
		}
		return data.value
	}
	return s.fallback.Get(key)
}

// New replaces the current value without invalidating pointers to old values.
func (s *OwnedSymbolLinks[V]) New(key *Symbol) *V {
	if data := s.owned(key); data != nil {
		if data.value == nil {
			s.ownedKeys = append(s.ownedKeys, key)
		}
		data.value = s.values.New()
		return data.value
	}
	return s.fallback.New(key)
}

func (s *OwnedSymbolLinks[V]) TryGet(key *Symbol) *V {
	if data := s.owned(key); data != nil {
		return data.value
	}
	return s.fallback.TryGet(key)
}

func (s *OwnedSymbolLinks[V]) Has(key *Symbol) bool { return s.TryGet(key) != nil }
