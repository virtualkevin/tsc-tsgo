package core

// PointerFilter is an insert-only, approximate membership filter with 65536 bits.
// False positives require an authoritative lookup; false negatives are forbidden.
// It retains no pointer roots. Inserted keys must have stable heap addresses.
// Its owner must retain inserted keys and use the
// pinned runtime's non-moving heap, as required by PointerLinkStore's hash.
// Mutation requires exclusive ownership. Do not clear bits while keys remain.
type PointerFilter[K any] struct {
	bits [1024]uint64
}

func (f *PointerFilter[K]) Add(key *K) {
	h := pointerLinkHash(key) & 65535
	f.bits[h>>6] |= uint64(1) << (h & 63)
}

func (f *PointerFilter[K]) MayContain(key *K) bool {
	h := pointerLinkHash(key) & 65535
	return f.bits[h>>6]&(uint64(1)<<(h&63)) != 0
}
