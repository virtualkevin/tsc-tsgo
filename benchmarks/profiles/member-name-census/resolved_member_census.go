package checker

import (
	"encoding/hex"
	"encoding/json"
	"math/bits"
	"os"
	"sort"
	"strings"
	"sync"

	"github.com/microsoft/typescript-go/internal/ast"
)

// Diagnostic counters only; bounded cloned names, no symbols, types or checkers retained.
// Updates use the owning checker's existing exclusive access.
type resolvedMemberPathCounts struct {
	Lookups, Hits, Misses                        uint64
	SizeBuckets, MissSizeBuckets, KeyByteBuckets [65]uint64
	MaxSize, MaxKeyBytes                         int
}
type resolvedMemberCensus struct {
	Owner                        int
	missNames                    map[string]uint64
	MissNames                    []resolvedMemberNameCount
	NameOverflow, LongNameMisses uint64
	// Paths: materialized table, frozen name layout, pending own, pending with bases.
	Paths [4]resolvedMemberPathCounts
}

const resolvedMemberNameLimit = 16384
const resolvedMemberNameBytes = 256

type resolvedMemberNameCount struct {
	NameHex string
	Count   uint64
}

func (s *resolvedMemberCensus) recordMissName(name string) {
	if len(name) > resolvedMemberNameBytes {
		s.LongNameMisses++
		return
	}
	if n, ok := s.missNames[name]; ok {
		s.missNames[name] = n + 1
		return
	}
	if len(s.missNames) == resolvedMemberNameLimit {
		s.NameOverflow++
		return
	}
	if s.missNames == nil {
		s.missNames = make(map[string]uint64)
	}
	s.missNames[strings.Clone(name)] = 1
}
func (s *resolvedMemberCensus) snapshotNames() {
	s.MissNames = make([]resolvedMemberNameCount, 0, len(s.missNames))
	for name, n := range s.missNames {
		s.MissNames = append(s.MissNames, resolvedMemberNameCount{hex.EncodeToString([]byte(name)), n})
	}
	sort.Slice(s.MissNames, func(i, j int) bool { return s.MissNames[i].NameHex < s.MissNames[j].NameHex })
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
	if path == 0 && symbol == nil {
		s.recordMissName(name)
	}
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
	for _, s := range resolvedMemberCensusRegistry.owners {
		s.snapshotNames()
	}
	data, err := json.MarshalIndent(struct {
		Scope  string
		Owners []*resolvedMemberCensus
	}{
		"Diagnostic counters; paths are materialized table, frozen name layout, pending own, pending with bases. Size is map entries, layout names, or own-source entries before lookup; pending size excludes inherited names. Buckets: zero is empty, k is [2^(k-1),2^k-1]. Key lengths are bytes. Hit means nonnil symbol, not map presence. Recursive calls count separately; nil-owner types are unobserved. Materialized nonnil-owner misses only: first 16384 distinct names of at most 256 bytes per owner retained as bounded clones, exact subsequent counts for admitted names. Other events counted in NameOverflow/LongNameMisses; overflow has insertion-order bias and is not a distinct-name count. Names serialized as hex to preserve invalid UTF-8 internal names. No table identities, unique requests, semantic objects, or timing claim.", resolvedMemberCensusRegistry.owners}, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(resolvedMemberCensusPath, append(data, '\n'), 0600)
}
