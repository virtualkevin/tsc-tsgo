package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func pendingNamesType(c *Checker, list []*ast.Symbol) (*StructuredType, *pendingInstantiatedMembers) {
	p := c.pendingInstantiatedList(list, nil)
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	return typ.AsStructuredType(), p
}

func TestPendingMemberNamesPropertiesAndLookupKeepIdentity(t *testing.T) {
	c := pendingTestChecker()
	list := []*ast.Symbol{c.newSymbol(ast.SymbolFlagsProperty, "z"), c.newSymbol(ast.SymbolFlagsProperty, "a")}
	typ, p := pendingNamesType(c, list)
	before := getResolvedMember(typ, "z")
	properties := typ.Properties()
	if len(properties) != 2 || properties[0].Name != "a" || properties[1] != before {
		t.Fatal("property order or earlier identity changed")
	}
	if typ.members != nil || typ.pendingMembers != p || p.memberNames == nil {
		t.Fatal("materialization retained the private symbol map")
	}
	if p.checker != nil || p.source != nil || p.mapper != nil || p.states != nil || p.bases != nil || p.instantiated != nil {
		t.Fatal("materialized pending state retains its inference/source/base graph")
	}
	count := c.SymbolCount
	if getResolvedMember(typ, "a") != properties[0] || getResolvedMember(typ, "z") != before || getResolvedMember(typ, "absent") != nil {
		t.Fatal("name layout lookup differs")
	}
	if typ.Properties()[1] != before || c.SymbolCount != count || typ.members != nil {
		t.Fatal("repeat access allocates or rebuilds the table")
	}
	table := typ.Members()
	if len(table) != 2 || table["z"] != before || table["a"] != properties[0] || typ.pendingMembers != nil || c.SymbolCount != count {
		t.Fatal("table reconstruction changes symbols")
	}
	added := c.newSymbol(ast.SymbolFlagsProperty, "added")
	table["added"] = added
	if getResolvedMember(typ, "added") != added {
		t.Fatal("table access did not restore ordinary mutable map behavior")
	}
}

func TestPendingMemberNamesShareLayoutAcrossSourceInstantiations(t *testing.T) {
	c := pendingTestChecker()
	list := []*ast.Symbol{c.newSymbol(ast.SymbolFlagsProperty, "a"), c.newSymbol(ast.SymbolFlagsProperty, "b")}
	first, p1 := pendingNamesType(c, list)
	second, p2 := pendingNamesType(c, list)
	first.Properties()
	second.Properties()
	if p1.memberNames == nil || p1.memberNames != p2.memberNames {
		t.Fatal("same source/order did not reuse layout")
	}
	if getResolvedMember(first, "a") == getResolvedMember(second, "a") {
		t.Fatal("different instantiations incorrectly share symbol instances")
	}
	changed, p3 := pendingNamesType(c, list)
	p3.hasBases = true
	p3.bases = []inheritedPendingMembers{{properties: []*ast.Symbol{c.newSymbol(ast.SymbolFlagsProperty, "c")}}}
	changed.Properties()
	if p3.bases != nil || p3.source != nil || p3.checker != nil {
		t.Fatal("inherited materialization retains pending graphs")
	}
	if resolvedPropertiesAreOptional(changed) {
		t.Fatal("clearing bases lost the required inherited property")
	}
	if p3.memberNames == p1.memberNames || getResolvedMember(changed, "c") == nil || getResolvedMember(first, "c") != nil {
		t.Fatal("changed inherited layout corrupted a previous instance")
	}
}

func TestPendingMemberNamesDuplicateAllocationOrder(t *testing.T) {
	c := pendingTestChecker()
	first := c.newSymbol(ast.SymbolFlagsProperty, "same")
	last := c.newSymbol(ast.SymbolFlagsProperty, "same")
	typ, _ := pendingNamesType(c, []*ast.Symbol{first, last})
	selected := getResolvedMember(typ, "same")
	before := c.SymbolCount
	properties := typ.Properties()
	if len(properties) != 1 || properties[0] != selected || c.SymbolCount != before+1 {
		t.Fatal("earlier duplicate must still instantiate before keeping final-name symbol")
	}
	if typ.Members()["same"] != selected || c.SymbolCount != before+1 {
		t.Fatal("reconstruction reinstantiated duplicate symbols")
	}
}

func TestPendingMemberNamesNonPropertiesAndResolvingStayEager(t *testing.T) {
	for _, mode := range []string{"internal", "resolving"} {
		t.Run(mode, func(t *testing.T) {
			c := pendingTestChecker()
			list := []*ast.Symbol{c.newSymbol(ast.SymbolFlagsProperty, "value")}
			if mode == "internal" {
				list = append(list, c.newSymbol(ast.SymbolFlagsMethod, ast.InternalSymbolNameCall))
			}
			typ, p := pendingNamesType(c, list)
			if mode == "resolving" {
				p.hasBases = true
				p.resolving = true
				p.bases = []inheritedPendingMembers{{properties: []*ast.Symbol{c.newSymbol(ast.SymbolFlagsProperty, "base")}}}
			}
			properties := typ.Properties()
			if len(properties) != 1 || typ.members == nil || typ.pendingMembers != nil || p.memberNames != nil {
				t.Fatal("unsafe table was dropped")
			}
			if mode == "internal" && typ.Members()[ast.InternalSymbolNameCall] == nil {
				t.Fatal("non-property member was lost")
			}
			if mode == "resolving" && typ.Members()["base"] == nil {
				t.Fatal("in-progress base table was lost")
			}
		})
	}
}

func TestPendingMemberNamesEmptyLayoutAndOrderValidation(t *testing.T) {
	c := pendingTestChecker()
	source := &InterfaceType{declaredMembers: ast.SymbolTable{ast.InternalSymbolNameCall: c.newSymbol(ast.SymbolFlagsMethod, ast.InternalSymbolNameCall)}}
	p := c.pendingInstantiatedTable(source, nil)
	if p == nil {
		t.Fatal("expected skipped reserved-member table")
	}
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	d := typ.AsStructuredType()
	if len(d.Properties()) != 0 || p.memberNames == nil || getResolvedMember(d, "absent") != nil {
		t.Fatal("empty layout not represented correctly")
	}
	if len(d.Members()) != 0 || d.pendingMembers != nil {
		t.Fatal("empty table reconstruction failed")
	}
	a := c.newSymbol(ast.SymbolFlagsProperty, "a")
	b := c.newSymbol(ast.SymbolFlagsProperty, "b")
	names := &memberNames{names: []string{"a", "b"}}
	if !hasMemberNames(names, []*ast.Symbol{a, b}) || hasMemberNames(names, []*ast.Symbol{b, a}) {
		t.Fatal("property order not checked")
	}
}
