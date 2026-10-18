package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func TestPropertyLoopCensusClasses(t *testing.T) {
	c := pendingTestChecker()
	if class, _ := propertyLoopClass(&Type{flags: TypeFlagsString}); class != 0 {
		t.Fatal(class)
	}
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	if class, _ := propertyLoopClass(typ); class != 1 {
		t.Fatal(class)
	}
	typ.objectFlags |= ObjectFlagsMembersResolved
	d := typ.AsStructuredType()
	d.pendingMembers = &pendingInstantiatedMembers{}
	if class, _ := propertyLoopClass(typ); class != 2 {
		t.Fatal(class)
	}
	d.pendingMembers = nil
	d.signatures = []*Signature{{}}
	if class, _ := propertyLoopClass(typ); class != 3 {
		t.Fatal(class)
	}
	d.signatures = nil
	typ.symbol = &ast.Symbol{Flags: ast.SymbolFlagsValueModule}
	if class, _ := propertyLoopClass(typ); class != 3 {
		t.Fatal(class)
	}
	typ.symbol = nil
	d.members = ast.SymbolTable{"x": nil}
	if class, size := propertyLoopClass(typ); class != 4 || size != 1 {
		t.Fatal(class, size)
	}
	typ.objectFlags |= ObjectFlagsUnresolvedMembers
	if class, _ := propertyLoopClass(typ); class != 1 {
		t.Fatal(class)
	}
}
func TestPropertyLoopCensusRecords(t *testing.T) {
	c := pendingTestChecker()
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	typ.objectFlags |= ObjectFlagsMembersResolved
	typ.AsStructuredType().members = ast.SymbolTable{"x": nil, "y": nil, "z": nil}
	s := &propertyLoopCensus{}
	o := s.begin(typ, nil, make([]*ast.Symbol, 8))
	target := &ast.Symbol{Flags: ast.SymbolFlagsOptional}
	o.counts.Visited += 4
	o.record(nil, target)
	o.record(target, target)
	o.record(&ast.Symbol{}, target)
	got := s.Classes[4]
	if got.Loops != 1 || got.Visited != 4 || got.Lookups != 3 || got.Misses != 1 || got.Hits != 2 || got.OptionalMisses != 1 || got.IdenticalHits != 1 {
		t.Fatal(got)
	}
	if s.OrdinaryLookups[2][4] != 3 || s.OrdinaryMisses[2][4] != 1 {
		t.Fatal("matrix buckets")
	}
}
func TestPropertyLoopCensusEntrySnapshotAndOwners(t *testing.T) {
	c := pendingTestChecker()
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	typ.objectFlags |= ObjectFlagsMembersResolved
	a, b := &propertyLoopCensus{}, &propertyLoopCensus{}
	o := a.begin(typ, nil, nil)
	typ.AsStructuredType().pendingMembers = &pendingInstantiatedMembers{}
	o.record(nil, &ast.Symbol{})
	q := b.begin(typ, nil, make([]*ast.Symbol, 1))
	q.record(&ast.Symbol{}, &ast.Symbol{})
	if a.Classes[4].Misses != 1 || a.OrdinaryMisses[0][0] != 1 || b.Classes[2].Hits != 1 || b.Classes[4].Lookups != 0 {
		t.Fatal("entry snapshot or owner mixing")
	}
}

func TestPropertyLoopCensusTargetLayout(t *testing.T) {
	c := pendingTestChecker()
	source := c.newObjectType(ObjectFlagsAnonymous, nil)
	source.objectFlags |= ObjectFlagsMembersResolved
	target := c.newObjectType(ObjectFlagsAnonymous, nil)
	props := make([]*ast.Symbol, 256)
	names := &memberNames{names: make([]string, 256)}
	target.AsStructuredType().pendingMembers = &pendingInstantiatedMembers{memberNames: names, materializedProperties: props}
	if !propertyLoopTargetLayout(target, props) {
		t.Fatal("existing layout")
	}
	if propertyLoopTargetLayout(target, props[:255]) || propertyLoopTargetLayout(target, make([]*ast.Symbol, 256)) || propertyLoopTargetLayout(nil, props) {
		t.Fatal("wrong snapshot")
	}
	s := &propertyLoopCensus{}
	o := s.begin(source, target, props)
	o.record(nil, &ast.Symbol{})
	if s.Classes[4].SmallWideLayoutMisses != 1 || s.Classes[4].LayoutLookups != 1 {
		t.Fatal("layout counters")
	}
	target.objectFlags |= ObjectFlagsMapped
	if propertyLoopTargetLayout(target, props) {
		t.Fatal("mapped target")
	}
}
