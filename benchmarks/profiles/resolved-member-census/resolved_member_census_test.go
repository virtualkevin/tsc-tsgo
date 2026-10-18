package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func TestResolvedMemberCensusBuckets(t *testing.T) {
	s := &resolvedMemberCensus{}
	for _, size := range []int{0, 1, 2, 3, 4, 7, 8} {
		s.record(0, size, size, size%2 == 0)
	}
	p := s.Paths[0]
	if p.Lookups != 7 || p.Hits != 4 || p.Misses != 3 || p.MaxSize != 8 || p.MaxKeyBytes != 8 {
		t.Fatal(p)
	}
	for i, want := range []uint64{1, 1, 2, 2, 1} {
		if p.SizeBuckets[i] != want || p.KeyByteBuckets[i] != want {
			t.Fatal("bucket boundary", i)
		}
	}
	if p.MissSizeBuckets[1] != 1 || p.MissSizeBuckets[2] != 1 || p.MissSizeBuckets[3] != 1 {
		t.Fatal("miss bucket")
	}
}
func TestResolvedMemberCensusPaths(t *testing.T) {
	s := &resolvedMemberCensus{}
	c := &Checker{resolvedMemberCensus: s}
	symbol := &ast.Symbol{Name: "é"}
	table := &StructuredType{members: ast.SymbolTable{"é": symbol, "nil": nil}}
	table.checker = c
	if getResolvedMember(table, "é") != symbol || getResolvedMember(table, "nil") != nil {
		t.Fatal("table behavior")
	}
	layout := &StructuredType{pendingMembers: &pendingInstantiatedMembers{memberNames: &memberNames{names: []string{"é"}, positions: map[string]int{"é": 0}}, materializedProperties: []*ast.Symbol{symbol}}}
	layout.checker = c
	if getResolvedMember(layout, "é") != symbol || getResolvedMember(layout, "absent") != nil {
		t.Fatal("layout behavior")
	}
	pending := &StructuredType{pendingMembers: &pendingInstantiatedMembers{checker: c, source: &instantiatedMemberSource{entries: []*ast.Symbol{symbol}, positions: map[string]int{"é": 0}}, states: []uint32{pendingMemberKept}}}
	pending.checker = c
	if getResolvedMember(pending, "é") != symbol || getResolvedMember(pending, "absent") != nil {
		t.Fatal("pending behavior")
	}
	inherited := &StructuredType{pendingMembers: &pendingInstantiatedMembers{checker: c, source: &instantiatedMemberSource{}, hasBases: true, bases: []inheritedPendingMembers{{properties: []*ast.Symbol{symbol}}}}}
	inherited.checker = c
	if getResolvedMember(inherited, "é") != symbol || getResolvedMember(inherited, "absent") != nil {
		t.Fatal("inherited behavior")
	}
	for i, p := range s.Paths {
		if p.Lookups != 2 || p.Hits != 1 || p.Misses != 1 {
			t.Fatal("path", i, p)
		}
	}
	if s.Paths[0].KeyByteBuckets[2] != 2 {
		t.Fatal("key lengths must be bytes")
	}
	if s.Paths[3].SizeBuckets[0] != 2 {
		t.Fatal("inherited names must not inflate own size")
	}
}
func TestResolvedMemberCensusDisabledAndOwners(t *testing.T) {
	symbol := &ast.Symbol{Name: "x"}
	s := &StructuredType{members: ast.SymbolTable{"x": symbol}}
	if getResolvedMember(s, "x") != symbol {
		t.Fatal("nil owner")
	}
	c := &Checker{}
	s.checker = c
	if getResolvedMember(s, "x") != symbol {
		t.Fatal("disabled observer")
	}
	first, second := &resolvedMemberCensus{}, &resolvedMemberCensus{}
	c.resolvedMemberCensus = first
	getResolvedMember(s, "x")
	c.resolvedMemberCensus = second
	getResolvedMember(s, "missing")
	if first.Paths[0].Hits != 1 || first.Paths[0].Misses != 0 || second.Paths[0].Hits != 0 || second.Paths[0].Misses != 1 {
		t.Fatal("owner counters mixed")
	}
}
