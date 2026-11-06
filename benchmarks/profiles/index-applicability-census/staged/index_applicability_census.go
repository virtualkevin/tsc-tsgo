package checker

import (
	"encoding/json"
	"os"
)

// Existing checker-local numeric type IDs; no Type roots or extra semantic queries.
type indexPair struct{ Source, Target TypeId }
type indexPairHistory struct {
	Completed uint64
	Last      bool
}
type indexBucket struct {
	SourceFlags, TargetFlags TypeFlags
	ActiveContext            bool
}
type indexRow struct {
	RepeatExclusiveInstantiations uint64
	RepeatExclusiveRelationGrowth int64
	indexBucket
	Calls, True, TrackedFirst, TrackedRepeat, Dropped, ChangedResult uint64
	InclusiveInstantiations, ExclusiveInstantiations                 uint64
	InclusiveRelationGrowth, ExclusiveRelationGrowth                 int64
}
type indexApplicabilityCensus struct {
	rows   map[indexBucket]*indexRow
	pairs  map[indexPair]indexPairHistory
	limit  int
	active *indexApplicabilityFrame
}
type indexApplicabilityFrame struct {
	bucket              indexBucket
	pair                indexPair
	tracked             bool
	parent              *indexApplicabilityFrame
	startInstantiations uint32
	startRelationSize   int
	childInstantiations uint64
	childRelationGrowth int64
}

func newIndexApplicabilityCensus() *indexApplicabilityCensus {
	if os.Getenv("TSC_GO_INDEX_APPLICABILITY_CENSUS") == "" {
		return nil
	}
	return &indexApplicabilityCensus{rows: make(map[indexBucket]*indexRow), pairs: make(map[indexPair]indexPairHistory), limit: 131072}
}
func (c *Checker) beginIndexApplicability(source, target *Type) *indexApplicabilityFrame {
	o := c.indexApplicabilityCensus
	pair := indexPair{source.id, target.id}
	_, tracked := o.pairs[pair]
	if !tracked && len(o.pairs) < o.limit {
		o.pairs[pair] = indexPairHistory{}
		tracked = true
	}
	frame := &indexApplicabilityFrame{bucket: indexBucket{source.flags, target.flags, c.instantiationDepth != 0 || len(c.activeMappers) != 0}, pair: pair, tracked: tracked, parent: o.active, startInstantiations: c.TotalInstantiationCount, startRelationSize: c.assignableRelation.size()}
	o.active = frame
	return frame
}
func (c *Checker) endIndexApplicability(frame *indexApplicabilityFrame, result bool) {
	o := c.indexApplicabilityCensus
	if o.active != frame {
		panic("index census stack mismatch")
	}
	o.active = frame.parent
	inst := uint64(c.TotalInstantiationCount - frame.startInstantiations)
	growth := int64(c.assignableRelation.size() - frame.startRelationSize)
	if inst < frame.childInstantiations {
		panic("index census instantiation partition")
	}
	if frame.parent != nil {
		frame.parent.childInstantiations += inst
		frame.parent.childRelationGrowth += growth
	}
	row := o.rows[frame.bucket]
	if row == nil {
		row = &indexRow{indexBucket: frame.bucket}
		o.rows[frame.bucket] = row
	}
	row.Calls++
	if result {
		row.True++
	}
	if frame.tracked {
		history := o.pairs[frame.pair]
		if history.Completed == 0 {
			row.TrackedFirst++
		} else {
			row.TrackedRepeat++
			row.RepeatExclusiveInstantiations += inst - frame.childInstantiations
			row.RepeatExclusiveRelationGrowth += growth - frame.childRelationGrowth
			if history.Last != result {
				row.ChangedResult++
			}
		}
		history.Completed++
		history.Last = result
		o.pairs[frame.pair] = history
	} else {
		row.Dropped++
	}
	row.InclusiveInstantiations += inst
	row.ExclusiveInstantiations += inst - frame.childInstantiations
	row.InclusiveRelationGrowth += growth
	row.ExclusiveRelationGrowth += growth - frame.childRelationGrowth
}

type IndexApplicabilitySnapshot struct {
	CheckerID               uint32
	Active                  bool
	PairLimit, TrackedPairs int
	Rows                    []indexRow
}

func (c *Checker) IndexApplicabilitySnapshot() (IndexApplicabilitySnapshot, bool) {
	o := c.indexApplicabilityCensus
	if o == nil {
		return IndexApplicabilitySnapshot{}, false
	}
	rows := make([]indexRow, 0, len(o.rows))
	for _, r := range o.rows {
		rows = append(rows, *r)
	}
	return IndexApplicabilitySnapshot{c.id, o.active != nil, o.limit, len(o.pairs), rows}, true
}
func WriteIndexApplicabilitySnapshots(path string, owners []IndexApplicabilitySnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Scope         string
		Owners        []IndexApplicabilitySnapshot
	}{1, "All isApplicableIndexType calls. Flag/context aggregates uncapped; first 131072 distinct numeric type-ID pairs per checker tracked, later unknown pairs dropped. Repeat means prior completed call (nested completion order), not semantic equivalence. IDs are checker-local, not shared origins. Relation size growth excludes replacements and does not prove no effects when zero. Instrumentation is not a speedup measurement.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
