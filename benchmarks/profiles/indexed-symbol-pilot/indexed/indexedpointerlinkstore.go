package core

// Sparse radix pages bound metadata by populated index regions, not by the
// greatest process-global index. Values and keys remain typed GC roots. The
// caller supplies a stable allocation handle; zero opts out of indexing.
// Distinct pointers carrying a copied handle use the pointer-key fallback.
// Mutation requires exclusive ownership. Populated copies may only be read.
type IndexedPointerLinkStore[K, V any] struct {
	root     [256]*indexedLinkDirectory[K, V]
	arena    Arena[V]
	fallback PointerLinkStore[K, V]
}

type indexedLinkDirectory[K, V any] [256]*indexedLinkBranch[K, V]
type indexedLinkBranch[K, V any] [256]*indexedLinkPage[K, V]
type indexedLinkPage[K, V any] [256]pointerLinkEntry[K, V]

func (s *IndexedPointerLinkStore[K, V]) entry(index uint32) *pointerLinkEntry[K, V] {
	directory := s.root[index>>24]
	if directory == nil {
		return nil
	}
	branch := directory[(index>>16)&255]
	if branch == nil {
		return nil
	}
	page := branch[(index>>8)&255]
	if page == nil {
		return nil
	}
	return &page[index&255]
}

func (s *IndexedPointerLinkStore[K, V]) ensureEntry(index uint32) *pointerLinkEntry[K, V] {
	directory := s.root[index>>24]
	if directory == nil {
		directory = new(indexedLinkDirectory[K, V])
		s.root[index>>24] = directory
	}
	branch := directory[(index>>16)&255]
	if branch == nil {
		branch = new(indexedLinkBranch[K, V])
		directory[(index>>16)&255] = branch
	}
	page := branch[(index>>8)&255]
	if page == nil {
		page = new(indexedLinkPage[K, V])
		branch[(index>>8)&255] = page
	}
	return &page[index&255]
}

func (s *IndexedPointerLinkStore[K, V]) Get(key *K, index uint32) *V {
	if index == 0 {
		return s.fallback.Get(key)
	}
	entry := s.entry(index)
	if entry != nil && entry.value != nil {
		if entry.key == key {
			return entry.value
		}
		return s.fallback.Get(key)
	}
	if entry == nil {
		entry = s.ensureEntry(index)
	}
	value := s.arena.New()
	*entry = pointerLinkEntry[K, V]{key: key, value: value}
	return value
}

func (s *IndexedPointerLinkStore[K, V]) New(key *K, index uint32) *V {
	if index == 0 {
		return s.fallback.New(key)
	}
	entry := s.ensureEntry(index)
	if entry.value != nil && entry.key != key {
		return s.fallback.New(key)
	}
	value := s.arena.New()
	*entry = pointerLinkEntry[K, V]{key: key, value: value}
	return value
}

func (s *IndexedPointerLinkStore[K, V]) TryGet(key *K, index uint32) *V {
	if index == 0 {
		return s.fallback.TryGet(key)
	}
	entry := s.entry(index)
	if entry == nil || entry.value == nil {
		return nil
	}
	if entry.key == key {
		return entry.value
	}
	return s.fallback.TryGet(key)
}

func (s *IndexedPointerLinkStore[K, V]) Has(key *K, index uint32) bool {
	return s.TryGet(key, index) != nil
}
