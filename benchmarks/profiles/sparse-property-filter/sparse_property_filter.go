package checker

import "github.com/microsoft/typescript-go/internal/ast"

// A local conservative name filter. Collisions only perform the original lookup.
// It is rebuilt after every lookup/comparison, never retained on a mutable type.
type sparsePropertyFilter [4]uint64

func sparsePropertyNameBit(name string) uint8 {
	if len(name) == 0 {
		return 0
	}
	// Only a fingerprint is needed; full string equality remains authoritative.
	h := uint32(len(name)) * 0x9e3779b1
	h ^= uint32(name[0]) * 0x85ebca6b
	h ^= uint32(name[len(name)-1]) * 0xc2b2ae35
	h ^= uint32(name[len(name)/2]) * 0x27d4eb2d
	h ^= h >> 16
	return uint8(h)
}
func (f *sparsePropertyFilter) add(name string) {
	bit := sparsePropertyNameBit(name)
	f[bit>>6] |= uint64(1) << (bit & 63)
}
func (f *sparsePropertyFilter) mayContain(name string) bool {
	bit := sparsePropertyNameBit(name)
	return f[bit>>6]&(uint64(1)<<(bit&63)) != 0
}

func sparsePropertyMembers(t *Type, limit int) (ast.SymbolTable, bool) {
	if t == nil || t.flags != TypeFlagsObject || t.objectFlags&ObjectFlagsMapped != 0 ||
		t.objectFlags&ObjectFlagsMembersResolved == 0 || t.objectFlags&ObjectFlagsUnresolvedMembers != 0 {
		return nil, false
	}
	d := t.AsStructuredType()
	if d.pendingMembers != nil || len(d.signatures) != 0 || len(d.members) > limit ||
		t.symbol != nil && t.symbol.Flags&ast.SymbolFlagsValueModule != 0 {
		return nil, false
	}
	return d.members, true
}
func (c *Checker) newSparsePropertyFilter(source *Type) (sparsePropertyFilter, bool) {
	var result sparsePropertyFilter
	// anyFunctionType receives Function augmentation even without signatures.
	if source == c.anyFunctionType {
		return result, false
	}
	own, ok := sparsePropertyMembers(source, 7)
	if !ok {
		return result, false
	}
	global, ok := sparsePropertyMembers(c.globalObjectType, 32)
	if !ok {
		return result, false
	}
	// All keys, including nil-valued/non-value entries, are conservative positives.
	for name := range own {
		result.add(name)
	}
	for name := range global {
		result.add(name)
	}
	return result, true
}
