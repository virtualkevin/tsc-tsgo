package checker

// relationKey is canonical: packed != 0 implies hash is zero. Packed keys are
// limited to non-generic template-key comparisons; other keys keep the full hash.
type relationKey struct {
	hash   CacheHashKey
	packed uint64
}

type tiledRelationResults struct {
	other         map[uint64]RelationComparisonResult
	tiles         map[uint64]*[4]uint64
	negativeCount int
}

func relationTileCoordinates(key uint64) (uint64, uint, uint64) {
	index := uint(((key>>32)&15)<<4 | ((key >> 2) & 15))
	return key &^ uint64(15<<32|15<<2), index >> 6, uint64(1) << (index & 63)
}
func (s *tiledRelationResults) get(key uint64) RelationComparisonResult {
	tile, word, mask := relationTileCoordinates(key)
	if block := s.tiles[tile]; block != nil && block[word]&mask != 0 {
		return RelationComparisonResultFailed
	}
	return s.other[key]
}
func (s *tiledRelationResults) set(key uint64, value RelationComparisonResult) {
	tile, word, mask := relationTileCoordinates(key)
	if value == RelationComparisonResultFailed {
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
	if block := s.tiles[tile]; block != nil && block[word]&mask != 0 {
		block[word] &^= mask
		s.negativeCount--
		if block[0]|block[1]|block[2]|block[3] == 0 {
			delete(s.tiles, tile)
		}
	}
	if s.other == nil {
		s.other = make(map[uint64]RelationComparisonResult)
	}
	s.other[key] = value
}
func (s *tiledRelationResults) size() int { return len(s.other) + s.negativeCount }
