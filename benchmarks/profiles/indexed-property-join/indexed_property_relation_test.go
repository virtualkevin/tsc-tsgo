package checker

import (
	"fmt"
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func indexedTestObject(c *Checker, names ...string) *Type {
	t := c.newObjectType(ObjectFlagsAnonymous, nil)
	t.objectFlags |= ObjectFlagsMembersResolved
	t.AsStructuredType().members = ast.SymbolTable{}
	for _, name := range names {
		t.AsStructuredType().members[name] = &ast.Symbol{Name: name, Flags: ast.SymbolFlagsProperty}
	}
	return t
}
func TestIndexedPropertyOrderAndMutation(t *testing.T) {
	c := pendingTestChecker()
	c.globalObjectType = indexedTestObject(c, "toString")
	source := indexedTestObject(c, "z", "a")
	layout := &memberNames{names: []string{"z", "absent", "toString", "a", "later"}, positions: map[string]int{"z": 0, "absent": 1, "toString": 2, "a": 3, "later": 4}}
	for cursor := 0; cursor <= len(layout.names); cursor++ {
		next, ok := c.nextIndexedProperty(source, layout, cursor)
		want := len(layout.names)
		for i := cursor; i < len(layout.names); i++ {
			name := layout.names[i]
			_, own := source.AsStructuredType().members[name]
			_, global := c.globalObjectType.AsStructuredType().members[name]
			if own || global {
				want = i
				break
			}
		}
		if !ok || next != want {
			t.Fatalf("cursor %d got %d/%v want %d", cursor, next, ok, want)
		}
	}
	// A recursive comparison can add an entry or replace the source member map.
	source.AsStructuredType().members = ast.SymbolTable{"later": nil}
	if next, ok := c.nextIndexedProperty(source, layout, 3); !ok || next != 4 {
		t.Fatal(next, ok)
	}
	c.globalObjectType.AsStructuredType().members["a"] = nil
	if next, ok := c.nextIndexedProperty(source, layout, 3); !ok || next != 3 {
		t.Fatal(next, ok)
	}
	source.AsStructuredType().pendingMembers = &pendingInstantiatedMembers{}
	if next, ok := c.nextIndexedProperty(source, layout, 3); ok || next != 3 {
		t.Fatal("fallback must preserve cursor", next, ok)
	}
}
func TestIndexedPropertyEligibility(t *testing.T) {
	c := pendingTestChecker()
	c.globalObjectType = indexedTestObject(c)
	layout := &memberNames{}
	for _, change := range []func(*Type){
		func(s *Type) { s.objectFlags |= ObjectFlagsMapped },
		func(s *Type) { s.objectFlags |= ObjectFlagsUnresolvedMembers },
		func(s *Type) { s.objectFlags &^= ObjectFlagsMembersResolved },
		func(s *Type) { s.AsStructuredType().signatures = []*Signature{{}} },
		func(s *Type) { s.symbol = &ast.Symbol{Flags: ast.SymbolFlagsValueModule} },
		func(s *Type) { c.anyFunctionType = s },
		func(s *Type) {
			for i := 0; i < 8; i++ {
				s.AsStructuredType().members[fmt.Sprint(i)] = nil
			}
		},
	} {
		s := indexedTestObject(c)
		change(s)
		if _, ok := c.nextIndexedProperty(s, layout, 0); ok {
			t.Fatal("unsafe source accepted")
		}
	}
	s := indexedTestObject(c)
	for i := 0; i < 33; i++ {
		c.globalObjectType.AsStructuredType().members[fmt.Sprint(i)] = nil
	}
	if _, ok := c.nextIndexedProperty(s, layout, 0); ok {
		t.Fatal("oversized global")
	}
}
func TestIndexedPropertyLayoutSnapshot(t *testing.T) {
	c := pendingTestChecker()
	target := indexedTestObject(c)
	properties := []*ast.Symbol{{Name: "z"}, {Name: "a"}}
	names := &memberNames{names: []string{"z", "a"}, positions: map[string]int{"z": 0, "a": 1}}
	p := &pendingInstantiatedMembers{memberNames: names, materializedProperties: properties}
	target.AsStructuredType().pendingMembers = p
	if indexedPropertyLayout(target, properties) != names {
		t.Fatal("valid snapshot")
	}
	copyProps := append([]*ast.Symbol(nil), properties...)
	if indexedPropertyLayout(target, copyProps) != nil {
		t.Fatal("different backing accepted")
	}
	if indexedPropertyLayout(target, properties[:1]) != nil {
		t.Fatal("different length accepted")
	}
	// Materializing the table clears pending storage, but a held immutable layout
	// remains valid for the original captured property slice.
	held := indexedPropertyLayout(target, properties)
	target.AsStructuredType().Members()
	if p.memberNames != nil || held.positions["a"] != 1 || properties[1].Name != "a" {
		t.Fatal("snapshot invalidated")
	}
	if indexedPropertyLayout(target, properties) != nil {
		t.Fatal("materialized table accepted")
	}
}
