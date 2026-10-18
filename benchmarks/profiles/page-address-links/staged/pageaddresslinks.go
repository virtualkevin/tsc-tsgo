package core

import (
	"runtime"
	"unsafe"
	"weak"
)

// PageAddressLinks is an isolated experiment, not the production link store.
// Allocation pages identify owned keys without adding fields to K. Integer
// addresses are only directory keys/offsets: pointers are never reconstructed.
// Like PointerLinkStore it assumes the pinned non-moving Go heap. Writes need
// exclusive ownership; populated stores may only be copied for read access.
type PageAddressLinks[K, V any] struct {
	directory map[uintptr][]*addressLinkPage[K, V]
	current   *[256]K
	used      int
	roots     []*K // Exactly the linked keys; unlinked pages have only weak roots.
	arena     Arena[V]
	fallback  PointerLinkStore[K, V]
}

type addressLinkPage[K, V any] struct {
	base   uintptr
	keys   weak.Pointer[[256]K]
	values []*V // Lazy, stable pointer slots; V itself uses the ordinary arena.
}

const addressLinkRegionShift = 16

func (s *PageAddressLinks[K, V]) NewKey() *K {
	var zero K
	if unsafe.Sizeof(zero) == 0 {
		return new(K)
	}
	if s.current == nil || s.used == len(s.current) {
		keys := new([256]K)
		base := uintptr(unsafe.Pointer(&keys[0]))
		page := &addressLinkPage[K, V]{base: base, keys: weak.Make(keys)}
		if s.directory == nil {
			s.directory = make(map[uintptr][]*addressLinkPage[K, V])
		}
		last := (base + unsafe.Sizeof(*keys) - 1) >> addressLinkRegionShift
		for region := base >> addressLinkRegionShift; region <= last; region++ {
			entries := s.directory[region]
			live := entries[:0]
			for _, old := range entries {
				if old.keys.Value() != nil {
					live = append(live, old)
				}
			}
			clear(entries[len(live):])
			s.directory[region] = append(live, page)
		}
		s.current, s.used = keys, 0
	}
	key := &s.current[s.used]
	s.used++
	return key
}

func (s *PageAddressLinks[K, V]) locate(key *K) (*addressLinkPage[K, V], int) {
	if key == nil {
		return nil, 0
	}
	var zero K
	stride := unsafe.Sizeof(zero)
	if stride == 0 {
		return nil, 0
	}
	addr := uintptr(unsafe.Pointer(key))
	defer runtime.KeepAlive(key)
	for _, page := range s.directory[addr>>addressLinkRegionShift] {
		offset := addr - page.base
		if offset >= 256*stride || offset%stride != 0 {
			continue
		}
		keys := page.keys.Value()
		index := int(offset / stride)
		if keys != nil && &keys[index] == key {
			return page, index
		}
	}
	return nil, 0
}

func (s *PageAddressLinks[K, V]) TryGet(key *K) *V {
	if page, index := s.locate(key); page != nil {
		if page.values == nil {
			return nil
		}
		return page.values[index]
	}
	return s.fallback.TryGet(key)
}
func (s *PageAddressLinks[K, V]) Has(key *K) bool { return s.TryGet(key) != nil }
func (s *PageAddressLinks[K, V]) put(page *addressLinkPage[K, V], index int, key *K) *V {
	if page.values == nil {
		page.values = make([]*V, 256)
	}
	if page.values[index] == nil {
		s.roots = append(s.roots, key)
	}
	value := s.arena.New()
	page.values[index] = value
	return value
}
func (s *PageAddressLinks[K, V]) Get(key *K) *V {
	if page, index := s.locate(key); page != nil {
		if page.values != nil && page.values[index] != nil {
			return page.values[index]
		}
		return s.put(page, index, key)
	}
	return s.fallback.Get(key)
}
func (s *PageAddressLinks[K, V]) New(key *K) *V {
	if page, index := s.locate(key); page != nil {
		return s.put(page, index, key)
	}
	return s.fallback.New(key)
}
