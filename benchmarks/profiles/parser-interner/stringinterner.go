package core

import "hash/maphash"

// StringInterner keeps the first string supplied for each distinct byte sequence.
// Its zero value is ready to use. Mutation requires exclusive ownership; readers
// may share a completed table. It must not be copied after its first insertion.
// Unlike a map[string]string, each nonempty string occupies only one slot.
type StringInterner struct {
	seed     maphash.Seed
	slots    []string
	count    int
	hasEmpty bool
}

func (s *StringInterner) Has(text string) bool {
	if s == nil {
		return false
	}
	if text == "" {
		return s.hasEmpty
	}
	if len(s.slots) == 0 {
		return false
	}
	mask := uint64(len(s.slots) - 1)
	for i := maphash.String(s.seed, text) & mask; ; i = (i + 1) & mask {
		key := s.slots[i]
		if key == text {
			return true
		}
		if key == "" {
			return false
		}
	}
}

func (s *StringInterner) Intern(text string) string {
	if text == "" {
		s.hasEmpty = true
		return text
	}
	if len(s.slots) == 0 {
		s.seed = maphash.MakeSeed()
		s.slots = make([]string, 8)
	}
	mask := uint64(len(s.slots) - 1)
	i := maphash.String(s.seed, text) & mask
	for s.slots[i] != "" {
		if s.slots[i] == text {
			return s.slots[i]
		}
		i = (i + 1) & mask
	}
	// Grow only for a genuinely new entry. Keep at least a quarter of slots empty.
	if s.count+1 > len(s.slots)*3/4 {
		old := s.slots
		s.slots = make([]string, len(old)*2)
		mask = uint64(len(s.slots) - 1)
		for _, key := range old {
			if key == "" {
				continue
			}
			j := maphash.String(s.seed, key) & mask
			for s.slots[j] != "" {
				j = (j + 1) & mask
			}
			s.slots[j] = key
		}
		i = maphash.String(s.seed, text) & mask
		for s.slots[i] != "" {
			i = (i + 1) & mask
		}
	}
	s.slots[i] = text
	s.count++
	return text
}
