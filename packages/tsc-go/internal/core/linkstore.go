package core

// Links store

type LinkStore[K comparable, V any] struct {
	entries map[K]*V
	arena   Arena[V]
}

func (s *LinkStore[K, V]) Get(key K) *V {
	value := s.entries[key]
	if value != nil {
		return value
	}
	if s.entries == nil {
		s.entries = make(map[K]*V)
	}
	value = s.arena.New()
	s.entries[key] = value
	return value
}

// New inserts a zero-valued entry for a key that has never been added to this
// store, without first looking it up. The caller must establish that the key is
// absent; use Get when it might already have links. As with Get, the returned
// pointer remains valid as the store grows.
func (s *LinkStore[K, V]) New(key K) *V {
	if s.entries == nil {
		s.entries = make(map[K]*V)
	}
	value := s.arena.New()
	s.entries[key] = value
	return value
}

func (s *LinkStore[K, V]) Has(key K) bool {
	_, ok := s.entries[key]
	return ok
}

func (s *LinkStore[K, V]) TryGet(key K) *V {
	return s.entries[key]
}
