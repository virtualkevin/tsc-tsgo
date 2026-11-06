package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"time"
)

type expressionRequestKey struct {
	Node       *ast.Node
	Context    TypeId
	NilContext bool
	Inference  *InferenceContext
	Mode       CheckMode
}
type expressionRequestHistory struct {
	Completed uint64
	Last      TypeId
	LastNil   bool
}
type expressionContextBucket struct {
	NodeKind                    ast.Kind
	Mode                        CheckMode
	ContextFlags                TypeFlags
	HasInference, ActiveContext bool
}
type expressionContextRow struct {
	expressionContextBucket
	Calls, NonNil, TrackedFirst, TrackedRepeat, Dropped, ChangedResult     uint64
	Inclusive, Exclusive, RepeatExclusive                                  [3]uint64 // instantiations, types, symbols
	InclusiveRelationGrowth, ExclusiveRelationGrowth, RepeatRelationGrowth int64
	InclusiveNs, ExclusiveNs                                               uint64
	InferenceSitesBefore, InferenceSitesAfter, ChangedInferenceFlags       uint64
}
type expressionContextCensus struct {
	rows     map[expressionContextBucket]*expressionContextRow
	requests map[expressionRequestKey]expressionRequestHistory
	limit    int
	active   *expressionContextFrame
}
type expressionContextFrame struct {
	key            expressionRequestKey
	bucket         expressionContextBucket
	tracked        bool
	parent         *expressionContextFrame
	start          [3]uint32
	child          [3]uint64
	relationStart  int
	childRelation  int64
	started        time.Time
	childNs        uint64
	inferenceSites int
	inferenceFlags InferenceFlags
}

func newExpressionContextCensus() *expressionContextCensus {
	if os.Getenv("TSC_GO_EXPRESSION_CONTEXT_CENSUS") == "" {
		return nil
	}
	return &expressionContextCensus{rows: make(map[expressionContextBucket]*expressionContextRow), requests: make(map[expressionRequestKey]expressionRequestHistory), limit: 131072}
}
func (c *Checker) expressionContextCounters() [3]uint32 {
	return [3]uint32{c.TotalInstantiationCount, c.TypeCount, c.SymbolCount}
}
func (c *Checker) expressionContextRelationSize() int {
	return c.assignableRelation.size() + c.subtypeRelation.size()
}
func (c *Checker) beginExpressionContext(node *ast.Node, contextual *Type, inference *InferenceContext, mode CheckMode) *expressionContextFrame {
	o := c.expressionContextCensus
	key := expressionRequestKey{Node: node, NilContext: contextual == nil, Inference: inference, Mode: mode}
	var kind ast.Kind
	if node != nil {
		kind = node.Kind
	}
	bucket := expressionContextBucket{NodeKind: kind, Mode: mode, HasInference: inference != nil, ActiveContext: c.instantiationDepth != 0 || len(c.activeMappers) != 0}
	if contextual != nil {
		key.Context = contextual.id
		bucket.ContextFlags = contextual.flags
	}
	_, tracked := o.requests[key]
	if !tracked && len(o.requests) < o.limit {
		o.requests[key] = expressionRequestHistory{}
		tracked = true
	}
	f := &expressionContextFrame{key: key, bucket: bucket, tracked: tracked, parent: o.active, start: c.expressionContextCounters(), relationStart: c.expressionContextRelationSize(), started: time.Now()}
	if inference != nil {
		f.inferenceSites = len(inference.intraExpressionInferenceSites)
		f.inferenceFlags = inference.flags
	}
	o.active = f
	return f
}
func (c *Checker) endExpressionContext(f *expressionContextFrame, result *Type) {
	o := c.expressionContextCensus
	if o.active != f {
		panic("JSX census stack mismatch")
	}
	o.active = f.parent
	elapsed := uint64(time.Since(f.started))
	if elapsed < f.childNs {
		panic("JSX census time partition")
	}
	end := c.expressionContextCounters()
	var inclusive, exclusive [3]uint64
	for i := range inclusive {
		inclusive[i] = uint64(end[i] - f.start[i])
		if inclusive[i] < f.child[i] {
			panic("JSX census counter partition")
		}
		exclusive[i] = inclusive[i] - f.child[i]
	}
	growth := int64(c.expressionContextRelationSize() - f.relationStart)
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
		row = &expressionContextRow{expressionContextBucket: f.bucket}
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

type ExpressionContextSnapshot struct {
	CheckerID                     uint32
	Active                        bool
	RequestLimit, TrackedRequests int
	Rows                          []expressionContextRow
}

func (c *Checker) ExpressionContextSnapshot() (ExpressionContextSnapshot, bool) {
	o := c.expressionContextCensus
	if o == nil {
		return ExpressionContextSnapshot{}, false
	}
	rows := make([]expressionContextRow, 0, len(o.rows))
	for _, r := range o.rows {
		rows = append(rows, *r)
	}
	return ExpressionContextSnapshot{c.id, o.active != nil, o.limit, len(o.requests), rows}, true
}
func WriteExpressionContextSnapshots(path string, owners []ExpressionContextSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Scope         string
		Owners        []ExpressionContextSnapshot
	}{1, "All checkExpressionWithContextualType requests whose input is not JsxAttributes. Uncapped aggregate rows; first 131072 distinct node/contextTypeID/inferencePointer/checkMode keys per checker tracked. Keys retain AST/inference graphs; IDs are checker-local; inference-pointer identity is not immutable state. Repeat means prior completion, not equivalence or reusable work. Counter slots are instantiations/types/symbols. Net relation growth covers assignable+subtype sizes, not replacements or all caches. Diagnostics, flow and inference state are not fully observed. Instrumented durations are not CPU/performance measurements.", owners}
	err = json.NewEncoder(f).Encode(report)
	closed := f.Close()
	if err != nil {
		return err
	}
	return closed
}
