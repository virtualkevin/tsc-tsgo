package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"time"
)

type jsxRequestKey struct {
	Node       *ast.Node
	Context    TypeId
	NilContext bool
	Inference  *InferenceContext
	Mode       CheckMode
}
type jsxRequestHistory struct {
	Completed uint64
	Last      TypeId
	LastNil   bool
}
type jsxContextBucket struct {
	Mode                        CheckMode
	ContextFlags                TypeFlags
	HasInference, ActiveContext bool
}
type jsxContextRow struct {
	jsxContextBucket
	Calls, NonNil, TrackedFirst, TrackedRepeat, Dropped, ChangedResult     uint64
	Inclusive, Exclusive, RepeatExclusive                                  [3]uint64 // instantiations, types, symbols
	InclusiveRelationGrowth, ExclusiveRelationGrowth, RepeatRelationGrowth int64
	InclusiveNs, ExclusiveNs                                               uint64
	InferenceSitesBefore, InferenceSitesAfter, ChangedInferenceFlags       uint64
}
type jsxContextCensus struct {
	rows     map[jsxContextBucket]*jsxContextRow
	requests map[jsxRequestKey]jsxRequestHistory
	limit    int
	active   *jsxContextFrame
}
type jsxContextFrame struct {
	key            jsxRequestKey
	bucket         jsxContextBucket
	tracked        bool
	parent         *jsxContextFrame
	start          [3]uint32
	child          [3]uint64
	relationStart  int
	childRelation  int64
	started        time.Time
	childNs        uint64
	inferenceSites int
	inferenceFlags InferenceFlags
}

func newJsxContextCensus() *jsxContextCensus {
	if os.Getenv("TSC_GO_JSX_CONTEXT_CENSUS") == "" {
		return nil
	}
	return &jsxContextCensus{rows: make(map[jsxContextBucket]*jsxContextRow), requests: make(map[jsxRequestKey]jsxRequestHistory), limit: 131072}
}
func (c *Checker) jsxContextCounters() [3]uint32 {
	return [3]uint32{c.TotalInstantiationCount, c.TypeCount, c.SymbolCount}
}
func (c *Checker) jsxContextRelationSize() int {
	return c.assignableRelation.size() + c.subtypeRelation.size()
}
func (c *Checker) beginJsxContext(node *ast.Node, contextual *Type, inference *InferenceContext, mode CheckMode) *jsxContextFrame {
	o := c.jsxContextCensus
	key := jsxRequestKey{Node: node, NilContext: contextual == nil, Inference: inference, Mode: mode}
	bucket := jsxContextBucket{Mode: mode, HasInference: inference != nil, ActiveContext: c.instantiationDepth != 0 || len(c.activeMappers) != 0}
	if contextual != nil {
		key.Context = contextual.id
		bucket.ContextFlags = contextual.flags
	}
	_, tracked := o.requests[key]
	if !tracked && len(o.requests) < o.limit {
		o.requests[key] = jsxRequestHistory{}
		tracked = true
	}
	f := &jsxContextFrame{key: key, bucket: bucket, tracked: tracked, parent: o.active, start: c.jsxContextCounters(), relationStart: c.jsxContextRelationSize(), started: time.Now()}
	if inference != nil {
		f.inferenceSites = len(inference.intraExpressionInferenceSites)
		f.inferenceFlags = inference.flags
	}
	o.active = f
	return f
}
func (c *Checker) endJsxContext(f *jsxContextFrame, result *Type) {
	o := c.jsxContextCensus
	if o.active != f {
		panic("JSX census stack mismatch")
	}
	o.active = f.parent
	elapsed := uint64(time.Since(f.started))
	if elapsed < f.childNs {
		panic("JSX census time partition")
	}
	end := c.jsxContextCounters()
	var inclusive, exclusive [3]uint64
	for i := range inclusive {
		inclusive[i] = uint64(end[i] - f.start[i])
		if inclusive[i] < f.child[i] {
			panic("JSX census counter partition")
		}
		exclusive[i] = inclusive[i] - f.child[i]
	}
	growth := int64(c.jsxContextRelationSize() - f.relationStart)
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
		row = &jsxContextRow{jsxContextBucket: f.bucket}
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
	row.InferenceSitesBefore += uint64(f.inferenceSites)
	if f.key.Inference != nil {
		row.InferenceSitesAfter += uint64(len(f.key.Inference.intraExpressionInferenceSites))
		if f.key.Inference.flags != f.inferenceFlags {
			row.ChangedInferenceFlags++
		}
	}
}

type JsxContextSnapshot struct {
	CheckerID                     uint32
	Active                        bool
	RequestLimit, TrackedRequests int
	Rows                          []jsxContextRow
}

func (c *Checker) JsxContextSnapshot() (JsxContextSnapshot, bool) {
	o := c.jsxContextCensus
	if o == nil {
		return JsxContextSnapshot{}, false
	}
	rows := make([]jsxContextRow, 0, len(o.rows))
	for _, r := range o.rows {
		rows = append(rows, *r)
	}
	return JsxContextSnapshot{c.id, o.active != nil, o.limit, len(o.requests), rows}, true
}
func WriteJsxContextSnapshots(path string, owners []JsxContextSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Scope         string
		Owners        []JsxContextSnapshot
	}{1, "All checkExpressionWithContextualType requests whose input is JsxAttributes. Uncapped aggregate rows; first 131072 distinct node/contextTypeID/inferencePointer/checkMode keys per checker tracked. Keys retain AST/inference graphs; IDs are checker-local; inference-pointer identity is not immutable state. Repeat means prior completion, not equivalence or reusable work. Counter slots are instantiations/types/symbols. Net relation growth covers assignable+subtype sizes, not replacements or all caches. Diagnostics, flow and inference state are not fully observed. Instrumented durations are not CPU/performance measurements.", owners}
	err = json.NewEncoder(f).Encode(report)
	closed := f.Close()
	if err != nil {
		return err
	}
	return closed
}
