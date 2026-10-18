package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"math/bits"
	"os"
	"sync"
)

type propertyLoopCounts struct{ Loops, Visited, Lookups, Hits, Misses, OptionalMisses, IdenticalHits uint64 }
type propertyLoopCensus struct {
	Owner                           int
	Classes                         [5]propertyLoopCounts
	OrdinaryLookups, OrdinaryMisses [65][65]uint64
}
type propertyLoopObservation struct {
	counts                     *propertyLoopCounts
	census                     *propertyLoopCensus
	sourceBucket, targetBucket int
	ordinary                   bool
}

var propertyLoopCensusPath = os.Getenv("TSC_GO_PROPERTY_LOOP_CENSUS")
var propertyLoopRegistry struct {
	sync.Mutex
	owners []*propertyLoopCensus
}

func newPropertyLoopCensus() *propertyLoopCensus {
	if propertyLoopCensusPath == "" {
		return nil
	}
	propertyLoopRegistry.Lock()
	defer propertyLoopRegistry.Unlock()
	s := &propertyLoopCensus{Owner: len(propertyLoopRegistry.owners) + 1}
	propertyLoopRegistry.owners = append(propertyLoopRegistry.owners, s)
	return s
}

// Classification only reads existing state; it never resolves or materializes a type.
// Ordinary is a shape observation, not a proof of immutable or safe-to-skip lookup.
func propertyLoopClass(source *Type) (int, int) {
	if source.flags&TypeFlagsObject == 0 {
		return 0, 0
	}
	if source.objectFlags&ObjectFlagsMembersResolved == 0 || source.objectFlags&ObjectFlagsUnresolvedMembers != 0 {
		return 1, 0
	}
	d := source.AsStructuredType()
	if d.pendingMembers != nil {
		return 2, 0
	}
	if len(d.signatures) != 0 || source.symbol != nil && source.symbol.Flags&ast.SymbolFlagsValueModule != 0 {
		return 3, len(d.members)
	}
	return 4, len(d.members)
}
func (s *propertyLoopCensus) begin(source *Type, targetSize int) propertyLoopObservation {
	class, size := propertyLoopClass(source)
	c := &s.Classes[class]
	c.Loops++
	return propertyLoopObservation{counts: c, census: s, sourceBucket: bits.Len(uint(size)), targetBucket: bits.Len(uint(targetSize)), ordinary: class == 4}
}
func (o propertyLoopObservation) record(source, target *ast.Symbol) {
	c := o.counts
	c.Lookups++
	if source != nil {
		c.Hits++
		if source == target {
			c.IdenticalHits++
		}
	} else {
		c.Misses++
		if target.Flags&ast.SymbolFlagsOptional != 0 {
			c.OptionalMisses++
		}
	}
	if o.ordinary {
		o.census.OrdinaryLookups[o.sourceBucket][o.targetBucket]++
		if source == nil {
			o.census.OrdinaryMisses[o.sourceBucket][o.targetBucket]++
		}
	}
}

// Called only after CLI checking. Checker-exclusive updates, no semantic objects retained.
func WritePropertyLoopCensus() error {
	if propertyLoopCensusPath == "" {
		return nil
	}
	propertyLoopRegistry.Lock()
	defer propertyLoopRegistry.Unlock()
	data, err := json.MarshalIndent(struct {
		Scope  string
		Owners []*propertyLoopCensus
	}{
		"Final propertiesRelatedTo loop only, after unmatched/fresh-object checks. Classes at loop entry: non-object, unresolved object, pending members, materialized callable/module, ordinary materialized object. Ordinary is not proven immutable. Target size before exclusions; source size raw member-map entries. Visited counts after exclusions, lookups after predicates, hits nonnil including identical symbols. Matrices count lookups/misses by initial source/target log2 size buckets: zero empty, k [2^(k-1),2^k-1]. Early exits and recursive loops counted as executed. Initial shape may change during comparisons. No forced resolution, names, semantic objects, unique pairs or timing claim.", propertyLoopRegistry.owners}, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(propertyLoopCensusPath, append(data, '\n'), 0600)
}
