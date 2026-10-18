package checker

import (
	"encoding/json"
	"math/bits"
	"os"
	"sync"
)

// Diagnostic-only counters. Each owner is accessed under the existing checker's
// exclusive ownership; the registry retains counters, never semantic objects.
type mergedLookupCensus struct {
	Owner                                    int
	Lookups, Replacements, Unchanged, Writes uint64
	PeakKeys                                 int
	// Bucket 0 is an empty map; bucket k covers [2^(k-1), 2^k-1].
	LookupSizeBuckets    [65]uint64
	UnchangedSizeBuckets [65]uint64
}

var mergedLookupCensusPath = os.Getenv("TSC_GO_MERGED_LOOKUP_CENSUS")
var mergedLookupCensusRegistry struct {
	sync.Mutex
	owners []*mergedLookupCensus
}

func newMergedLookupCensus() *mergedLookupCensus {
	if mergedLookupCensusPath == "" {
		return nil
	}
	mergedLookupCensusRegistry.Lock()
	defer mergedLookupCensusRegistry.Unlock()
	s := &mergedLookupCensus{Owner: len(mergedLookupCensusRegistry.owners) + 1}
	mergedLookupCensusRegistry.owners = append(mergedLookupCensusRegistry.owners, s)
	return s
}

func (s *mergedLookupCensus) lookup(size int, replacement bool) {
	s.Lookups++
	bucket := bits.Len(uint(size))
	s.LookupSizeBuckets[bucket]++
	if replacement {
		s.Replacements++
	} else {
		s.Unchanged++
		s.UnchangedSizeBuckets[bucket]++
	}
}

// Call only after all CLI checking has completed. Registry locking does not
// permit concurrent snapshots of an actively used checker.
func WriteMergedLookupCensus() error {
	if mergedLookupCensusPath == "" {
		return nil
	}
	mergedLookupCensusRegistry.Lock()
	defer mergedLookupCensusRegistry.Unlock()
	data, err := json.MarshalIndent(struct {
		Scope  string
		Owners []*mergedLookupCensus
	}{"Diagnostic observer; unchanged means absent or nil replacement, not proven map absence. Nil input bypasses lookup. No semantic keys retained. Counts are not CPU costs or timing evidence.", mergedLookupCensusRegistry.owners}, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(mergedLookupCensusPath, append(data, '\n'), 0600)
}
