// Package tilednegativeprototype is an isolated storage experiment. It is not
// connected to the compiler and does not establish key-construction equivalence.
package tilednegativeprototype

const Failed uint32 = 2
const fallbackTag uint64 = 1 << 63
const idLimit uint64 = 1 << 30
const lowCoordinateMask uint64 = 15<<32 | 15<<2

// Store preserves map[uint64]uint32 observations including present zero values
// in Size. Only canonical packed keys with a plain Failed result use tiles.
// Zero-value ready; single-owner mutation. Copying a populated Store is unsupported.
// Keys must be supplied by a separately validated compiler key implementation.
type Store struct {
	other         map[uint64]uint32
	tiles         map[uint64]*[4]uint64
	negativeCount int
}

func coordinates(key uint64) (tile uint64, word uint, mask uint64, eligible bool) {
	source := key >> 32
	target := (key >> 2) & (idLimit - 1)
	if source == 0 || source >= idLimit || target == 0 {
		return 0, 0, 0, false
	}
	index := uint((source&15)<<4 | (target & 15))
	return key &^ lowCoordinateMask, index >> 6, uint64(1) << (index & 63), true
}
func (s *Store) Get(key uint64) uint32 {
	if tile, word, mask, ok := coordinates(key); ok {
		if block := s.tiles[tile]; block != nil && block[word]&mask != 0 {
			return Failed
		}
	}
	return s.other[key]
}
func (s *Store) Set(key uint64, value uint32) {
	tile, word, mask, eligible := coordinates(key)
	if eligible && value == Failed {
		delete(s.other, key)
		if s.tiles == nil {
			s.tiles = make(map[uint64]*[4]uint64)
		}
		block := s.tiles[tile]
		if block == nil {
			block = new([4]uint64)
			s.tiles[tile] = block
		}
		if block[word]&mask == 0 {
			block[word] |= mask
			s.negativeCount++
		}
		return
	}
	if eligible {
		if block := s.tiles[tile]; block != nil && block[word]&mask != 0 {
			block[word] &^= mask
			s.negativeCount--
			if block[0]|block[1]|block[2]|block[3] == 0 {
				delete(s.tiles, tile)
			}
		}
	}
	if s.other == nil {
		s.other = make(map[uint64]uint32)
	}
	s.other[key] = value
}
func (s *Store) Size() int { return len(s.other) + s.negativeCount }
