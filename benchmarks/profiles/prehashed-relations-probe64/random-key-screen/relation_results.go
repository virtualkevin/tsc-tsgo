package main

// Relation keys are already full-width hashes. Keep both words for equality;
// their low bits only choose the first probe slot. No semantic key is narrowed.
const relationResultProbeLimit = 64
const relationResultInitialCapacity = 8

type relationResultCache struct {
	keys     []CacheHashKey
	values   []RelationComparisonResult
	occupied []uint64
	count    int
	// Permanent fallback bounds pathological probe chains while retaining the
	// runtime map's randomized hashing. A zero result is still a stored entry.
	fallback map[CacheHashKey]RelationComparisonResult
}

func (s *relationResultCache) get(key CacheHashKey) RelationComparisonResult {
	if s == nil {
		return RelationComparisonResultNone
	}
	if s.fallback != nil {
		return s.fallback[key]
	}
	if slot, found := s.find(key); found {
		return s.values[slot]
	}
	return RelationComparisonResultNone
}

func (s *relationResultCache) size() int {
	if s == nil {
		return 0
	}
	return s.count
}

func (s *relationResultCache) hasSlot(slot int) bool {
	return s.occupied[slot>>6]&(uint64(1)<<uint(slot&63)) != 0
}

// find is read-only. Every inserted key is at distance less than the probe
// limit, so exhausting it also proves absence without scanning the whole table.
func (s *relationResultCache) find(key CacheHashKey) (int, bool) {
	if len(s.keys) == 0 {
		return -1, false
	}
	mask := len(s.keys) - 1
	slot := int(key.Lo & uint64(mask))
	for range min(len(s.keys), relationResultProbeLimit) {
		if !s.hasSlot(slot) {
			return slot, false
		}
		if s.keys[slot] == key {
			return slot, true
		}
		slot = (slot + 1) & mask
	}
	return -1, false
}

func (s *relationResultCache) writeSlot(slot int, found bool, key CacheHashKey, value RelationComparisonResult) {
	if !found {
		s.keys[slot] = key
		s.occupied[slot>>6] |= uint64(1) << uint(slot&63)
		s.count++
	}
	s.values[slot] = value
}

func (s *relationResultCache) set(key CacheHashKey, value RelationComparisonResult) {
	if s.fallback != nil {
		s.fallback[key] = value
		s.count = len(s.fallback)
		return
	}
	if len(s.keys) == 0 {
		*s = newRelationResultTable(relationResultInitialCapacity)
	}
	slot, found := s.find(key)
	if found {
		// Replacement never grows the table, even at its load threshold.
		s.values[slot] = value
		return
	}
	if slot < 0 {
		s.useFallback(key, value)
		return
	}
	if s.count >= len(s.keys)-len(s.keys)/4 {
		capacity, ok := nextRelationResultCapacity(len(s.keys))
		if !ok {
			s.useFallback(key, value)
			return
		}
		s.rebuild(capacity, key, value)
		return
	}
	s.writeSlot(slot, false, key, value)
}

// Use division before multiplication so both the doubling and the largest
// backing allocation (16-byte keys) remain representable on the target int.
func nextRelationResultCapacity(capacity int) (int, bool) {
	maxInt := int(^uint(0) >> 1)
	if capacity < relationResultInitialCapacity || capacity&(capacity-1) != 0 || capacity > maxInt/16/2 {
		return 0, false
	}
	return capacity * 2, true
}

func newRelationResultTable(capacity int) relationResultCache {
	return relationResultCache{
		keys:     make([]CacheHashKey, capacity),
		values:   make([]RelationComparisonResult, capacity),
		occupied: make([]uint64, (capacity+63)/64),
	}
}

// rebuild publishes only a complete table. If reinsertion or the pending write
// exceeds the probe bound, fallback is built from ALL original entries instead.
func (s *relationResultCache) rebuild(capacity int, key CacheHashKey, value RelationComparisonResult) {
	next := newRelationResultTable(capacity)
	for i, oldKey := range s.keys {
		if s.hasSlot(i) {
			slot, found := next.find(oldKey)
			if slot < 0 {
				s.useFallback(key, value)
				return
			}
			next.writeSlot(slot, found, oldKey, s.values[i])
		}
	}
	slot, found := next.find(key)
	if slot < 0 {
		s.useFallback(key, value)
		return
	}
	next.writeSlot(slot, found, key, value)
	*s = next
}

func (s *relationResultCache) useFallback(key CacheHashKey, value RelationComparisonResult) {
	fallback := make(map[CacheHashKey]RelationComparisonResult, s.count+1)
	for i, oldKey := range s.keys {
		if s.hasSlot(i) {
			fallback[oldKey] = s.values[i]
		}
	}
	fallback[key] = value
	*s = relationResultCache{fallback: fallback, count: len(fallback)}
}
