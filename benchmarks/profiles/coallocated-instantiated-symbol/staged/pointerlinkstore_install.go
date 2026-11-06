package core

// Install publishes caller-owned typed storage, preserving old published values
// on replacement. A nil value cannot represent a populated slot and is rejected
// before any mutation. Mutation requires exclusive ownership, just like New.
func (s *PointerLinkStore[K, V]) Install(key *K, value *V) {
	if value == nil {
		panic("PointerLinkStore.Install: nil value")
	}
	if len(s.entries) == 0 {
		s.grow()
	}
	index := s.slot(key)
	if s.entries[index].value == nil {
		if s.count+1 > len(s.entries)-len(s.entries)/4 {
			s.grow()
			index = s.slot(key)
		}
		s.count++
	}
	s.entries[index] = pointerLinkEntry[K, V]{key: key, value: value}
}
