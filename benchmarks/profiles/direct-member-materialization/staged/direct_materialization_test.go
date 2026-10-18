package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"slices"
	"testing"
)

func directTestNames(names ...string) *memberNames {
	n := &memberNames{names: names, positions: make(map[string]int, len(names))}
	for i, s := range names {
		n.positions[s] = i
	}
	return n
}
func TestDirectMaterializationDuplicateIdentity(t *testing.T) {
	c := pendingTestChecker()
	first := c.newSymbol(ast.SymbolFlagsProperty, "same")
	last := c.newSymbol(ast.SymbolFlagsProperty, "same")
	base := c.newSymbol(ast.SymbolFlagsProperty, "base")
	override := c.newSymbol(ast.SymbolFlagsProperty, "same")
	p := c.pendingInstantiatedList([]*ast.Symbol{first, last}, nil)
	p.source.lastMemberNames = directTestNames("base", "same")
	p.hasBases = true
	p.bases = []inheritedPendingMembers{{properties: []*ast.Symbol{base, override}}}
	selected := p.ownMember("same")
	before := c.SymbolCount
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	properties := typ.AsStructuredType().Properties()
	if len(properties) != 2 || properties[0] != base || properties[1] != selected || c.SymbolCount != before+1 {
		t.Fatal("identity, inheritance or duplicate allocation order changed")
	}
	if p.checker != nil || p.source != nil || p.mapper != nil || p.bases != nil || p.instantiated != nil {
		t.Fatal("construction graph retained")
	}
	table := typ.AsStructuredType().Members()
	if table["same"] != selected || table["base"] != base || c.SymbolCount != before+1 {
		t.Fatal("API table reconstruction changed symbols")
	}
}
func TestDirectMaterializationFallback(t *testing.T) {
	for _, layout := range [][]string{{"z", "a"}, {"a", "z", "missing"}, {"a"}} {
		t.Run(layout[0]+string(rune('0'+len(layout))), func(t *testing.T) {
			c := pendingTestChecker()
			a := c.newSymbol(ast.SymbolFlagsProperty, "a")
			z := c.newSymbol(ast.SymbolFlagsProperty, "z")
			p := c.pendingInstantiatedList([]*ast.Symbol{z, a}, nil)
			p.source.lastMemberNames = directTestNames(layout...)
			before := c.SymbolCount
			typ := c.newObjectType(ObjectFlagsAnonymous, nil)
			c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
			props := typ.AsStructuredType().Properties()
			if len(props) != 2 || props[0].Name != "a" || props[1].Name != "z" || c.SymbolCount != before+2 {
				t.Fatal("fallback replayed construction or changed order")
			}
			if !slices.Equal(p.memberNames.names, []string{"a", "z"}) {
				t.Fatal("wrong replacement layout")
			}
		})
	}
}
func TestDirectMaterializationInheritedReplacement(t *testing.T) {
	c := pendingTestChecker()
	nonvalue := c.newSymbol(ast.SymbolFlagsInterface, "x")
	value := c.newSymbol(ast.SymbolFlagsProperty, "x")
	p := c.pendingInstantiatedList([]*ast.Symbol{nonvalue}, nil)
	p.source.lastMemberNames = directTestNames("x")
	p.hasBases = true
	p.bases = []inheritedPendingMembers{{properties: []*ast.Symbol{value}}}
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	props := typ.AsStructuredType().Properties()
	if len(props) != 1 || props[0] != value {
		t.Fatal("inherited value must replace nonvalue")
	}
}
func TestDirectMaterializationRecursiveAndEmpty(t *testing.T) {
	c := pendingTestChecker()
	own := c.newSymbol(ast.SymbolFlagsProperty, "own")
	base := c.newSymbol(ast.SymbolFlagsProperty, "base")
	p := c.pendingInstantiatedList([]*ast.Symbol{own}, nil)
	p.source.lastMemberNames = directTestNames("base", "own")
	p.hasBases, p.resolving = true, true
	p.bases = []inheritedPendingMembers{{properties: []*ast.Symbol{base}}}
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	props := typ.AsStructuredType().Properties()
	if len(props) != 1 || props[0].Name != "own" || typ.AsStructuredType().pendingMembers != nil {
		t.Fatal("recursive path must expose own properties and mutable table")
	}
	if len(typ.AsStructuredType().Members()) != 2 {
		t.Fatal("recursive table lost base")
	}
	source := &InterfaceType{declaredMembers: ast.SymbolTable{"type": c.newSymbol(ast.SymbolFlagsInterface, "type")}}
	empty := c.pendingInstantiatedTable(source, nil)
	source.instantiatedMemberSource.lastMemberNames = directTestNames()
	other := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(other, empty, nil, nil, nil)
	if other.AsStructuredType().Properties() != nil {
		t.Fatal("empty properties must remain nil")
	}
	if len(other.AsStructuredType().Members()) != 0 {
		t.Fatal("empty table changed")
	}
}
