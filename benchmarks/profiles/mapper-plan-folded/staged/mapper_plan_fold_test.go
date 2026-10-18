package checker

import "testing"

func TestMapperPlanFoldedExhaustive(t *testing.T) {
	a, b, other := &Type{}, &Type{}, &Type{}
	domain := []*Type{nil, a, b}
	// All 9^4 sequences of four pointer substitutions, including cycles,
	// duplicate sources, identity substitutions, nil targets and absent keys.
	for encoded := 0; encoded < 6561; encoded++ {
		n := encoded
		var root *TypeMapper
		for i := 0; i < 4; i++ {
			pair := n % 9
			n /= 9
			leaf := newSimpleTypeMapper(domain[pair/3], domain[pair%3])
			if root == nil {
				root = leaf
			} else {
				root = newMergedTypeMapper(root, leaf)
			}
		}
		p := compileMapperExecutionPlan(root)
		if p == nil || p.code[0].op != mapperPlanFolded {
			t.Fatal("not folded")
		}
		for _, input := range []*Type{nil, a, b, other} {
			if p.Map(input) != root.Map(input) {
				t.Fatalf("sequence %d", encoded)
			}
		}
	}
}
func TestMapperPlanFoldedBranchBoundary(t *testing.T) {
	a, b, c, d := &Type{}, &Type{}, &Type{}, &Type{}
	// A changed composite skips its RHS instructions and must enter the tail.
	// Folding RHS and tail into a single span would skip required substitutions.
	rhs := newMergedTypeMapper(newSimpleTypeMapper(b, c), newSimpleTypeMapper(c, b))
	inner := newCompositeTypeMapper(nil, newSimpleTypeMapper(a, b), rhs)
	tail := newMergedTypeMapper(newSimpleTypeMapper(b, c), newSimpleTypeMapper(c, d))
	root := newMergedTypeMapper(inner, tail)
	p := compileMapperExecutionPlan(root)
	for _, input := range []*Type{a, b, c, d, nil} {
		callsOld, callsNew := 0, 0
		old := mapperPlanReference(root, input, func(_ *Checker, t *Type, m *TypeMapper) *Type { callsOld++; return m.Map(t) })
		got := p.execute(input, func(_ *Checker, t *Type, m *TypeMapper) *Type { callsNew++; return m.Map(t) })
		if old != got || callsOld != callsNew {
			t.Fatal("branch entry/effects changed")
		}
	}
}
