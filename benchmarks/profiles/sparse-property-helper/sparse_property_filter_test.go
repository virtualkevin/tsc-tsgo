package checker

import (
	"fmt"
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func sparseFilterObject(c *Checker, names ...string) *Type {
	t := c.newObjectType(ObjectFlagsAnonymous, nil)
	t.objectFlags |= ObjectFlagsMembersResolved
	t.AsStructuredType().members = ast.SymbolTable{}
	for _, name := range names {
		t.AsStructuredType().members[name] = &ast.Symbol{Name: name, Flags: ast.SymbolFlagsProperty}
	}
	return t
}
func TestSparsePropertyFilterConservative(t *testing.T) {
	var f sparsePropertyFilter
	names := []string{"", "children", "toString", "é", "\xfe@iterator@12"}
	for i := 0; i < 1024; i++ {
		names = append(names, fmt.Sprint(i))
	}
	for _, name := range names {
		f.add(name)
		if !f.mayContain(name) {
			t.Fatal("new false negative", name)
		}
	}
	for _, name := range names {
		if !f.mayContain(name) {
			t.Fatal("retained false negative", name)
		}
	}
	// Find a collision and require it to remain a possible member.
	byBit := map[uint8]string{}
	for i := 0; i < 1024; i++ {
		name := fmt.Sprint(i)
		b := sparsePropertyNameBit(name)
		if prev, ok := byBit[b]; ok {
			var g sparsePropertyFilter
			g.add(prev)
			if !g.mayContain(name) {
				t.Fatal("collision rejected")
			}
			return
		}
		byBit[b] = name
	}
	t.Fatal("pigeonhole collision missing")
}
func TestSparsePropertyFilterEligibility(t *testing.T) {
	c := pendingTestChecker()
	c.globalObjectType = sparseFilterObject(c, "toString")
	s := sparseFilterObject(c, "x")
	if _, ok := c.newSparsePropertyFilter(s); !ok {
		t.Fatal("ordinary")
	}
	for _, flags := range []ObjectFlags{ObjectFlagsMapped, ObjectFlagsUnresolvedMembers} {
		s.objectFlags |= flags
		if _, ok := c.newSparsePropertyFilter(s); ok {
			t.Fatal(flags)
		}
		s.objectFlags &^= flags
	}
	s.objectFlags &^= ObjectFlagsMembersResolved
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("unresolved")
	}
	s.objectFlags |= ObjectFlagsMembersResolved
	s.AsStructuredType().pendingMembers = &pendingInstantiatedMembers{}
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("pending")
	}
	s.AsStructuredType().pendingMembers = nil
	s.AsStructuredType().signatures = []*Signature{{}}
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("callable")
	}
	s.AsStructuredType().signatures = nil
	s.symbol = &ast.Symbol{Flags: ast.SymbolFlagsValueModule}
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("module")
	}
	s.symbol = nil
	c.anyFunctionType = s
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("any function")
	}
	c.anyFunctionType = nil
	for i := 0; i < 8; i++ {
		s.AsStructuredType().members[fmt.Sprint(i)] = nil
	}
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("source size")
	}
	if _, ok := c.newSparsePropertyFilter(&Type{flags: TypeFlagsString}); ok {
		t.Fatal("primitive")
	}
}
func TestSparsePropertyFilterAugmentationAndRefresh(t *testing.T) {
	c := pendingTestChecker()
	c.globalObjectType = sparseFilterObject(c, "toString")
	s := sparseFilterObject(c, "x")
	f, ok := c.newSparsePropertyFilter(s)
	if !ok || !f.mayContain("x") || !f.mayContain("toString") {
		t.Fatal("augmentation")
	}
	// Simulate mutations during lookup/recursive comparison, then refresh.
	s.AsStructuredType().members["newSource"] = nil
	c.globalObjectType.AsStructuredType().members["newGlobal"] = nil
	f, ok = c.newSparsePropertyFilter(s)
	if !ok || !f.mayContain("newSource") || !f.mayContain("newGlobal") {
		t.Fatal("refresh")
	}
	s.AsStructuredType().pendingMembers = &pendingInstantiatedMembers{}
	if _, ok = c.newSparsePropertyFilter(s); ok {
		t.Fatal("mutation must fall back")
	}
}
func TestSparsePropertyFilterGlobalFallback(t *testing.T) {
	c := pendingTestChecker()
	s := sparseFilterObject(c)
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("nil global")
	}
	c.globalObjectType = sparseFilterObject(c)
	for i := 0; i < 32; i++ {
		c.globalObjectType.AsStructuredType().members[fmt.Sprint(i)] = nil
	}
	if _, ok := c.newSparsePropertyFilter(s); !ok {
		t.Fatal("global limit boundary")
	}
	c.globalObjectType.AsStructuredType().members["extra"] = nil
	if _, ok := c.newSparsePropertyFilter(s); ok {
		t.Fatal("oversize global")
	}
}
