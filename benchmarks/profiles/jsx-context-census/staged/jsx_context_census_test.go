package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"path/filepath"
	"testing"
)

func jsxCensusChecker(t *testing.T) *Checker {
	t.Setenv("TSC_GO_JSX_CONTEXT_CENSUS", "enabled")
	return &Checker{jsxContextCensus: newJsxContextCensus(), assignableRelation: &Relation{}, subtypeRelation: &Relation{}}
}
func TestJsxContextNestedCompletion(t *testing.T) {
	c := jsxCensusChecker(t)
	node := &ast.Node{Kind: ast.KindJsxAttributes}
	typ := &Type{id: 1}
	outer := c.beginJsxContext(node, typ, nil, CheckModeNormal)
	c.TotalInstantiationCount += 2
	c.TypeCount += 2
	c.SymbolCount += 2
	inner := c.beginJsxContext(node, typ, nil, CheckModeNormal)
	c.TotalInstantiationCount += 3
	c.TypeCount += 3
	c.SymbolCount += 3
	c.endJsxContext(inner, typ)
	c.TotalInstantiationCount += 4
	c.TypeCount += 4
	c.SymbolCount += 4
	c.endJsxContext(outer, &Type{id: 2})
	s, _ := c.JsxContextSnapshot()
	r := s.Rows[0]
	if s.Active || s.TrackedRequests != 1 || r.Calls != 2 || r.TrackedFirst != 1 || r.TrackedRepeat != 1 || r.ChangedResult != 1 || r.Inclusive != [3]uint64{12, 12, 12} || r.Exclusive != [3]uint64{9, 9, 9} || r.RepeatExclusive != [3]uint64{6, 6, 6} || r.ExclusiveNs > r.InclusiveNs {
		t.Fatal(s)
	}
}
func TestJsxContextKeyAndCap(t *testing.T) {
	c := jsxCensusChecker(t)
	c.jsxContextCensus.limit = 4
	node := &ast.Node{Kind: ast.KindJsxAttributes}
	typ := &Type{id: 1}
	a, b := &InferenceContext{}, &InferenceContext{}
	for _, x := range []struct {
		ctx  *Type
		inf  *InferenceContext
		mode CheckMode
	}{{nil, nil, 0}, {&Type{id: 0}, nil, 0}, {typ, a, 0}, {typ, b, 0}, {typ, a, CheckModeInferential}, {typ, a, 0}} {
		frame := c.beginJsxContext(node, x.ctx, x.inf, x.mode)
		c.endJsxContext(frame, typ)
	}
	s, _ := c.JsxContextSnapshot()
	var first, repeat, dropped uint64
	for _, r := range s.Rows {
		first += r.TrackedFirst
		repeat += r.TrackedRepeat
		dropped += r.Dropped
	}
	if s.TrackedRequests != 4 || first != 4 || repeat != 1 || dropped != 1 {
		t.Fatal(s)
	}
}
func TestJsxContextEffectsAndExclusiveOutput(t *testing.T) {
	c := jsxCensusChecker(t)
	ctx := &InferenceContext{}
	node := &ast.Node{Kind: ast.KindJsxAttributes}
	frame := c.beginJsxContext(node, nil, ctx, 0)
	ctx.flags = InferenceFlagsAnyDefault
	c.assignableRelation.results = map[CacheHashKey]RelationComparisonResult{{}: RelationComparisonResultSucceeded}
	c.endJsxContext(frame, nil)
	frame = c.beginJsxContext(node, nil, ctx, 0)
	c.assignableRelation.results = nil
	c.endJsxContext(frame, nil)
	s, _ := c.JsxContextSnapshot()
	r := s.Rows[0]
	if r.ChangedInferenceFlags != 1 || r.ExclusiveRelationGrowth != 0 || r.RepeatRelationGrowth != -1 || r.NonNil != 0 {
		t.Fatal(r)
	}
	path := filepath.Join(t.TempDir(), "census.json")
	if err := WriteJsxContextSnapshots(path, []JsxContextSnapshot{s}); err != nil {
		t.Fatal(err)
	}
	before, _ := os.ReadFile(path)
	if err := WriteJsxContextSnapshots(path, nil); err == nil {
		t.Fatal("overwrote output")
	}
	after, _ := os.ReadFile(path)
	if string(before) != string(after) {
		t.Fatal("modified output")
	}
}
