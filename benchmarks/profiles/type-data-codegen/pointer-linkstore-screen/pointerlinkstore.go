package core

import "unsafe"

// PointerLinkStore is an experimental pointer-key links table. Keys and values
// remain typed GC roots, and values retain their arena allocation across growth.
// Address hashing requires the pinned Go runtime's non-moving heap; a moving
// collector would require a stable hash or rehash notification. Like LinkStore,
// writes require exclusive ownership; existing-key Get and TryGet/Has are reads.
// Do not independently mutate copies of a populated arena-backed store.
type PointerLinkStore[K, V any] struct {
	entries []pointerLinkEntry[K, V]
	count   int
	arena   Arena[V]
}

type pointerLinkEntry[K, V any] struct {
	key   *K
	value *V // nil marks an empty slot, allowing a nil key to be stored
}

func pointerLinkHash[K any](key *K) uint64 {
	// One-way conversion only. Never reconstruct a pointer from the hash.
	// Mix high address bits as well as aligned arena strides before masking.
	x := uint64(uintptr(unsafe.Pointer(key)))
	x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9
	x = (x ^ (x >> 27)) * 0x94d049bb133111eb
	return x ^ (x >> 31)
}

func (s *PointerLinkStore[K, V]) slot(key *K) int {
	mask := len(s.entries) - 1
	index := int(pointerLinkHash(key) & uint64(mask))
	for range len(s.entries) {
		entry := &s.entries[index]
		if entry.value == nil || entry.key == key {
			return index
		}
		index = (index + 1) & mask
	}
	panic("PointerLinkStore has no empty slot")
}

func (s *PointerLinkStore[K, V]) grow() {
	capacity := len(s.entries)
	if capacity == 0 {
		capacity = 16
	} else {
		if capacity > int(^uint(0)>>1)/2 {
			panic("PointerLinkStore capacity overflow")
		}
		capacity *= 2
	}
	// Build before publication. Rehash preserves every arena value pointer.
	next := PointerLinkStore[K, V]{entries: make([]pointerLinkEntry[K, V], capacity)}
	for _, entry := range s.entries {
		if entry.value != nil {
			next.entries[next.slot(entry.key)] = entry
		}
	}
	s.entries = next.entries
}

func (s *PointerLinkStore[K, V]) insertAt(key *K, index int) *V {
	if len(s.entries) == 0 {
		s.grow()
		index = s.slot(key)
	} else if s.entries[index].value == nil && s.count+1 > len(s.entries)-len(s.entries)/4 {
		s.grow()
		index = s.slot(key)
	}
	value := s.arena.New()
	if s.entries[index].value == nil {
		s.count++
	}
	s.entries[index] = pointerLinkEntry[K, V]{key: key, value: value}
	return value
}

func (s *PointerLinkStore[K, V]) Get(key *K) *V {
	index := 0
	if len(s.entries) != 0 {
		index = s.slot(key)
		if value := s.entries[index].value; value != nil {
			return value
		}
	}
	return s.insertAt(key, index)
}

// New installs a fresh zero-valued entry. Callers should establish key absence;
// a duplicate nevertheless replaces its entry, matching LinkStore.New.
func (s *PointerLinkStore[K, V]) New(key *K) *V {
	index := 0
	if len(s.entries) != 0 {
		index = s.slot(key)
	}
	return s.insertAt(key, index)
}

func (s *PointerLinkStore[K, V]) TryGet(key *K) *V {
	if len(s.entries) == 0 {
		return nil
	}
	return s.entries[s.slot(key)].value
}

func (s *PointerLinkStore[K, V]) Has(key *K) bool {
	return s.TryGet(key) != nil
}
