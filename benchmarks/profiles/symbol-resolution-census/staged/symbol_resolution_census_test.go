package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func censusChecker() *Checker {
	c := pendingTestChecker()
	c.symbolResolutionCensus = &symbolResolutionCensus{Origins: make(map[string]*symbolResolutionRecord)}
	return c
}
func TestSymbolResolutionCensusNestedCounts(t *testing.T) {
	c := censusChecker()
	a := c.newSymbol(ast.SymbolFlagsProperty, "a")
	b := c.newSymbol(ast.SymbolFlagsProperty, "b")
	outer := c.beginSymbolResolution(a, 5)
	c.TotalInstantiationCount += 2
	inner := c.beginSymbolResolution(b, 5)
	c.TotalInstantiationCount += 3
	typ := &Type{flags: TypeFlagsString}
	c.endSymbolResolution(inner, typ, true)
	c.TotalInstantiationCount += 4
	c.endSymbolResolution(outer, typ, true)
	if outer.record.InclusiveInstantiations != 9 || outer.record.ExclusiveInstantiations != 6 || inner.record.ExclusiveInstantiations != 3 || c.symbolResolutionCensus.active != nil {
		t.Fatal("nested partition")
	}
	if outer.record.InclusiveNs < outer.record.ExclusiveNs || outer.record.Calls != 1 || inner.record.Completed != 1 {
		t.Fatal("accounting")
	}
}
func TestSymbolResolutionCensusOriginsDoNotForceIDs(t *testing.T) {
	a := &ast.Symbol{Name: "a", Flags: ast.SymbolFlagsProperty}
	b := &ast.Symbol{Name: "a", Flags: ast.SymbolFlagsProperty}
	if symbolResolutionOrigin(a, 5, 0, 0) != symbolResolutionOrigin(b, 5, 0, 0) {
		t.Fatal("pointer identity leaked")
	}
	node := &ast.Node{Kind: ast.KindPropertySignature}
	node.Parent = node
	a.Declarations = []*ast.Node{node}
	var d symbolOriginDescriptor
	if err := json.Unmarshal([]byte(symbolResolutionOrigin(a, 5, 0, 0)), &d); err != nil || !d.Unresolved {
		t.Fatal("cycle not unclassified")
	}
	if symbolResolutionOrigin(b, 5, 0, 0) == symbolResolutionOrigin(b, 5, 1, 0) {
		t.Fatal("context shape collapsed")
	}
}
func TestSymbolResolutionCensusHitAndMiss(t *testing.T) {
	c := censusChecker()
	original := c.newSymbol(ast.SymbolFlagsProperty, "p")
	typ := &Type{flags: TypeFlagsString}
	c.valueSymbolLinks.Get(original).resolvedType = typ
	clone := c.newInstantiatedSymbol(original, nil)
	if c.getTypeOfSymbol(clone) != typ || c.getTypeOfSymbol(clone) != typ {
		t.Fatal("type changed")
	}
	o := c.symbolResolutionCensus
	if o.Misses[1] != 1 || o.Hits[1] != 1 || o.Hits[5] != 1 || o.Misses[5] != 0 {
		t.Fatal("cache classification", o.Hits, o.Misses)
	}
	for _, r := range o.Origins {
		if r.Completed != 1 || r.Cached != 1 {
			t.Fatal("completion")
		}
	}
}
