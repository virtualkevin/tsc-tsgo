package checker

import (
	"encoding/json"

	"os"
	"time"
)

type discriminantRequestKey struct {
	Type TypeId
	Name string
}
type discriminantRequestHistory struct {
	Completed uint64
	Last      TypeId
	LastNil   bool
}
type discriminantQueryBucket struct {
	Kind          uint8
	TypeFlags     TypeFlags
	ObjectFlags   ObjectFlags
	ActiveContext bool
}
type discriminantQueryRow struct {
	discriminantQueryBucket
	Calls, NonNil, TrackedFirst, TrackedRepeat, Dropped, ChangedResult     uint64
	Inclusive, Exclusive, RepeatExclusive                                  [3]uint64 // instantiations, types, symbols
	InclusiveRelationGrowth, ExclusiveRelationGrowth, RepeatRelationGrowth int64
	InclusiveNs, ExclusiveNs                                               uint64
}
type discriminantQueryCensus struct {
	rows     map[discriminantQueryBucket]*discriminantQueryRow
	requests map[discriminantRequestKey]discriminantRequestHistory
	limit    int
	active   *discriminantQueryFrame
}
type discriminantQueryFrame struct {
	key           discriminantRequestKey
	bucket        discriminantQueryBucket
	tracked       bool
	parent        *discriminantQueryFrame
	start         [3]uint32
	child         [3]uint64
	relationStart int
	childRelation int64
	started       time.Time
	childNs       uint64
}

func newDiscriminantQueryCensus() *discriminantQueryCensus {
	if os.Getenv("TSC_GO_DISCRIMINANT_QUERY_CENSUS") == "" {
		return nil
	}
	return &discriminantQueryCensus{rows: make(map[discriminantQueryBucket]*discriminantQueryRow), requests: make(map[discriminantRequestKey]discriminantRequestHistory), limit: 131072}
}
func (c *Checker) discriminantQueryCounters() [3]uint32 {
	return [3]uint32{c.TotalInstantiationCount, c.TypeCount, c.SymbolCount}
}
func (c *Checker) discriminantQueryRelationSize() int {
	return c.assignableRelation.size() + c.subtypeRelation.size()
}
func (c *Checker) beginDiscriminantQuery(t *Type, name string, discriminator Discriminator) *discriminantQueryFrame {
	o := c.discriminantQueryCensus
	key := discriminantRequestKey{t.id, name}
	kind := uint8(0)
	switch discriminator.(type) {
	case *TypeDiscriminator:
		kind = 1
	case *ObjectLiteralDiscriminator:
		kind = 2
	}
	bucket := discriminantQueryBucket{kind, t.flags, t.objectFlags, c.instantiationDepth != 0 || len(c.activeMappers) != 0}

	_, tracked := o.requests[key]
	if !tracked && len(o.requests) < o.limit {
		o.requests[key] = discriminantRequestHistory{}
		tracked = true
	}
	f := &discriminantQueryFrame{key: key, bucket: bucket, tracked: tracked, parent: o.active, start: c.discriminantQueryCounters(), relationStart: c.discriminantQueryRelationSize(), started: time.Now()}
	o.active = f
	return f
}
func (c *Checker) endDiscriminantQuery(f *discriminantQueryFrame, result *Type) {
	o := c.discriminantQueryCensus
	if o.active != f {
		panic("discriminant query census stack mismatch")
	}
	o.active = f.parent
	elapsed := uint64(time.Since(f.started))
	if elapsed < f.childNs {
		panic("discriminant query census time partition")
	}
	end := c.discriminantQueryCounters()
	var inclusive, exclusive [3]uint64
	for i := range inclusive {
		inclusive[i] = uint64(end[i] - f.start[i])
		if inclusive[i] < f.child[i] {
			panic("discriminant query census counter partition")
		}
		exclusive[i] = inclusive[i] - f.child[i]
	}
	growth := int64(c.discriminantQueryRelationSize() - f.relationStart)
	exclusiveGrowth := growth - f.childRelation
	if f.parent != nil {
		for i := range inclusive {
			f.parent.child[i] += inclusive[i]
		}
		f.parent.childRelation += growth
		f.parent.childNs += elapsed
	}
	row := o.rows[f.bucket]
	if row == nil {
		row = &discriminantQueryRow{discriminantQueryBucket: f.bucket}
		o.rows[f.bucket] = row
	}
	row.Calls++
	var id TypeId
	if result != nil {
		row.NonNil++
		id = result.id
	}
	if f.tracked {
		history := o.requests[f.key]
		if history.Completed == 0 {
			row.TrackedFirst++
		} else {
			row.TrackedRepeat++
			for i := range exclusive {
				row.RepeatExclusive[i] += exclusive[i]
			}
			row.RepeatRelationGrowth += exclusiveGrowth
			if history.Last != id || history.LastNil != (result == nil) {
				row.ChangedResult++
			}
		}
		history.Completed++
		history.Last = id
		history.LastNil = result == nil
		o.requests[f.key] = history
	} else {
		row.Dropped++
	}
	for i := range inclusive {
		row.Inclusive[i] += inclusive[i]
		row.Exclusive[i] += exclusive[i]
	}
	row.InclusiveRelationGrowth += growth
	row.ExclusiveRelationGrowth += exclusiveGrowth
	row.InclusiveNs += elapsed
	row.ExclusiveNs += elapsed - f.childNs
}

type DiscriminantQuerySnapshot struct {
	CheckerID                     uint32
	Active                        bool
	RequestLimit, TrackedRequests int
	Rows                          []discriminantQueryRow
}

func (c *Checker) DiscriminantQuerySnapshot() (DiscriminantQuerySnapshot, bool) {
	o := c.discriminantQueryCensus
	if o == nil {
		return DiscriminantQuerySnapshot{}, false
	}
	rows := make([]discriminantQueryRow, 0, len(o.rows))
	for _, r := range o.rows {
		rows = append(rows, *r)
	}
	return DiscriminantQuerySnapshot{c.id, o.active != nil, o.limit, len(o.requests), rows}, true
}
func WriteDiscriminantQuerySnapshots(path string, owners []DiscriminantQuerySnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Scope         string
		Owners        []DiscriminantQuerySnapshot
	}{1, "Only property-or-index queries directly dispatched by discriminateTypeByDiscriminableItems. Aggregates uncapped; first 131072 distinct checker-local type-ID/property-name pairs tracked. Keys deliberately omit mutable context, augmentation state and caller; repetition is not semantic equivalence. Names retained; no Type roots or extra semantic queries. Nested completed observations are subtracted for exclusive work. Counter and assignable/subtype size deltas are incomplete effects; zero does not prove purity. Timings are instrumented, not workload performance", owners}
	err = json.NewEncoder(f).Encode(report)
	closed := f.Close()
	if err != nil {
		return err
	}
	return closed
}

func (c *Checker) observedDiscriminantQuery(t *Type, name string, discriminator Discriminator) (result *Type) {
	if c.discriminantQueryCensus != nil {
		frame := c.beginDiscriminantQuery(t, name, discriminator)
		defer func() { c.endDiscriminantQuery(frame, result) }()
	}
	return c.getTypeOfPropertyOrIndexSignatureOfType(t, name)
}
