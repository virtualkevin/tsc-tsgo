package checker

import (
	"encoding/json"
	"math/bits"
	"os"
	"sync"

	"github.com/microsoft/typescript-go/internal/ast"
)

// Diagnostic counters only; no queried keys, symbols, types or checkers retained.
// Updates use the owning checker's existing exclusive access.
type resolvedMemberPathCounts struct {
	Lookups, Hits, Misses                        uint64
	SizeBuckets, MissSizeBuckets, KeyByteBuckets [65]uint64
	MaxSize, MaxKeyBytes                         int
}
type resolvedMemberCensus struct {
	Owner int
	// Paths: materialized table, frozen name layout, pending own, pending with bases.
	Paths [4]resolvedMemberPathCounts
}

var resolvedMemberCensusPath = os.Getenv("TSC_GO_RESOLVED_MEMBER_CENSUS")
var resolvedMemberCensusRegistry struct {
	sync.Mutex
	owners []*resolvedMemberCensus
}

func newResolvedMemberCensus() *resolvedMemberCensus {
	if resolvedMemberCensusPath == "" {
		return nil
	}
	resolvedMemberCensusRegistry.Lock()
	defer resolvedMemberCensusRegistry.Unlock()
	s := &resolvedMemberCensus{Owner: len(resolvedMemberCensusRegistry.owners) + 1}
	resolvedMemberCensusRegistry.owners = append(resolvedMemberCensusRegistry.owners, s)
	return s
}
func (s *resolvedMemberCensus) record(path, size, keyBytes int, hit bool) {
	p := &s.Paths[path]
	p.Lookups++
	p.SizeBuckets[bits.Len(uint(size))]++
	p.KeyByteBuckets[bits.Len(uint(keyBytes))]++
	p.MaxSize = max(p.MaxSize, size)
	p.MaxKeyBytes = max(p.MaxKeyBytes, keyBytes)
	if hit {
		p.Hits++
	} else {
		p.Misses++
		p.MissSizeBuckets[bits.Len(uint(size))]++
	}
}
func getResolvedMemberObserved(t *StructuredType, name string, s *resolvedMemberCensus) *ast.Symbol {
	// Snapshot path/size before lazy resolution, which may change pending state.
	path, size := 0, len(t.members)
	var symbol *ast.Symbol
	if p := t.pendingMembers; p != nil {
		if p.memberNames != nil {
			path = 1
			size = len(p.memberNames.names)
		} else {
			path = 2
			if p.hasBases {
				path = 3
			}
			size = len(p.source.entries)
		}
		symbol = p.get(name)
	} else {
		symbol = t.members[name]
	}
	s.record(path, size, len(name), symbol != nil)
	return symbol
}

// Only after CLI checking completes; registry locking does not synchronize
// snapshots with active owners. Recursive base lookups count as separate calls.
func WriteResolvedMemberCensus() error {
	if resolvedMemberCensusPath == "" {
		return nil
	}
	resolvedMemberCensusRegistry.Lock()
	defer resolvedMemberCensusRegistry.Unlock()
	data, err := json.MarshalIndent(struct {
		Scope  string
		Owners []*resolvedMemberCensus
	}{
		"Diagnostic counters; paths are materialized table, frozen name layout, pending own, pending with bases. Size is map entries, layout names, or own-source entries before lookup; pending size excludes inherited names. Buckets: zero is empty, k is [2^(k-1),2^k-1]. Key lengths are bytes. Hit means nonnil symbol, not map presence. Recursive calls count separately; nil-owner types are unobserved. No names/semantic objects retained; no unique-name counts or timing claim.", resolvedMemberCensusRegistry.owners}, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(resolvedMemberCensusPath, append(data, '\n'), 0600)
}
