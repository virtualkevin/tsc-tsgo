package core

// DensePointerLinks is an isolated storage experiment. Numeric probe slots do
// not contain GC pointers. Typed entries retain every linked key and current
// value; returned values remain in the ordinary arena across table growth.
// It inherits pointerLinkHash's pinned non-moving-heap assumption. Mutations
// require exclusive ownership, and populated copies are read-only aliases.
type DensePointerLinks[K, V any] struct {
	slots   []uint32 // Dense entry index plus one; zero denotes empty, including nil keys.
	entries []pointerLinkEntry[K, V]
	arena   Arena[V]
}

func (s *DensePointerLinks[K, V]) slot(key *K) int {
	mask := len(s.slots) - 1
	index := int(pointerLinkHash(key) & uint64(mask))
	for range len(s.slots) {
		id := s.slots[index]
		if id == 0 || s.entries[id-1].key == key {
			return index
		}
		index = (index + 1) & mask
	}
	panic("DensePointerLinks has no empty slot")
}
func (s *DensePointerLinks[K, V]) grow() {
	capacity := len(s.slots)
	if capacity == 0 {
		capacity = 16
	} else {
		if capacity > int(^uint(0)>>1)/2 {
			panic("DensePointerLinks capacity overflow")
		}
		capacity *= 2
	}
	// Reserve exactly the load threshold: no additional append-growth policy.
	next := DensePointerLinks[K, V]{slots: make([]uint32, capacity), entries: make([]pointerLinkEntry[K, V], len(s.entries), capacity-capacity/4)}
	copy(next.entries, s.entries)
	for i, entry := range next.entries {
		next.slots[next.slot(entry.key)] = uint32(i) + 1
	}
	s.slots, s.entries = next.slots, next.entries
}
func (s *DensePointerLinks[K, V]) insert(key *K, index int) *V {
	if len(s.slots) == 0 {
		s.grow()
		index = s.slot(key)
	}
	id := s.slots[index]
	if id == 0 {
		if uint64(len(s.entries)) >= uint64(^uint32(0)) {
			panic("DensePointerLinks index overflow")
		}
		if len(s.entries) == cap(s.entries) {
			s.grow()
			index = s.slot(key)
		}
		value := s.arena.New()
		s.entries = append(s.entries, pointerLinkEntry[K, V]{key: key, value: value})
		s.slots[index] = uint32(len(s.entries))
		return value
	}
	value := s.arena.New()
	s.entries[id-1].value = value
	return value
}
func (s *DensePointerLinks[K, V]) Get(key *K) *V {
	index := 0
	if len(s.slots) != 0 {
		index = s.slot(key)
		if id := s.slots[index]; id != 0 {
			return s.entries[id-1].value
		}
	}
	return s.insert(key, index)
}
func (s *DensePointerLinks[K, V]) New(key *K) *V {
	index := 0
	if len(s.slots) != 0 {
		index = s.slot(key)
	}
	return s.insert(key, index)
}
func (s *DensePointerLinks[K, V]) TryGet(key *K) *V {
	if len(s.slots) == 0 {
		return nil
	}
	if id := s.slots[s.slot(key)]; id != 0 {
		return s.entries[id-1].value
	}
	return nil
}
func (s *DensePointerLinks[K, V]) Has(key *K) bool { return s.TryGet(key) != nil }
