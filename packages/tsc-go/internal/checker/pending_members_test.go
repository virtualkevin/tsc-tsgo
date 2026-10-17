package checker

import (
	"fmt"
	"strings"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
)

func pendingTestChecker() *Checker {
	c := &Checker{compareSymbols: func(a, b *ast.Symbol) int { return strings.Compare(a.Name, b.Name) }}
	c.couldContainTypeVariables = c.couldContainTypeVariablesWorker
	return c
}

func TestPendingMembersSnapshotKeepAndClone(t *testing.T) {
	c := pendingTestChecker()
	primitive := &Type{flags: TypeFlagsString}
	unresolved := c.newSymbol(ast.SymbolFlagsProperty, "unresolved")
	resolved := c.newSymbol(ast.SymbolFlagsProperty, "resolved")
	setter := c.newSymbol(ast.SymbolFlagsSetAccessor, "setter")
	c.valueSymbolLinks.Get(resolved).resolvedType = primitive
	c.valueSymbolLinks.Get(setter).resolvedType = primitive
	p := c.pendingInstantiatedList([]*ast.Symbol{unresolved, resolved, setter}, nil)
	// Later type resolution must not turn an original clone decision into reuse.
	c.valueSymbolLinks.Get(unresolved).resolvedType = primitive
	c.valueSymbolLinks.Get(setter).writeType = primitive
	if c.instantiateSymbol(unresolved, nil) != unresolved || c.instantiateSymbol(setter, nil) != setter {
		t.Fatal("test setup should now permit reuse")
	}
	for _, symbol := range []*ast.Symbol{unresolved, setter} {
		got := p.ownMember(symbol.Name)
		if got == symbol || c.valueSymbolLinks.Get(got).target != symbol {
			t.Fatalf("%s lost its frozen clone decision", symbol.Name)
		}
		if p.ownMember(symbol.Name) != got {
			t.Fatalf("%s changed identity on repeated lookup", symbol.Name)
		}
	}
	if p.ownMember(resolved.Name) != resolved {
		t.Fatal("resolved primitive symbol must be kept")
	}
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	before := p.ownMember(unresolved.Name)
	members := typ.AsStructuredType().Members()
	if members[unresolved.Name] != before {
		t.Fatal("enumeration replaced a previously returned symbol")
	}
	if len(typ.AsStructuredType().Properties()) != 3 {
		t.Fatal("properties were not materialized")
	}
}

func TestPendingMembersFrozenMapPositions(t *testing.T) {
	c := pendingTestChecker()
	primitive := &Type{flags: TypeFlagsNumber}
	source := &InterfaceType{declaredMembers: make(ast.SymbolTable)}
	for i := 0; i < 80; i++ {
		name := fmt.Sprintf("member%02d", i)
		symbol := c.newSymbol(ast.SymbolFlagsProperty, name)
		source.declaredMembers[name] = symbol
		if i%3 == 0 {
			c.valueSymbolLinks.Get(symbol).resolvedType = primitive
		}
	}
	var shared *instantiatedMemberSource
	for round := 0; round < 20; round++ {
		p := c.pendingInstantiatedTable(source, nil)
		if p == nil {
			t.Fatal("expected deferred members")
		}
		if shared != nil && p.source != shared {
			t.Fatal("instantiations did not share the frozen entry order")
		}
		shared = p.source
		for i := 79; i >= 0; i-- {
			name := fmt.Sprintf("member%02d", i)
			got := p.ownMember(name)
			if (got == source.declaredMembers[name]) != (i%3 == 0) {
				t.Fatalf("state/name mismatch at %s, round %d", name, round)
			}
		}
	}
	source.declaredMembers = ast.SymbolTable{"mismatched": c.newSymbol(ast.SymbolFlagsProperty, "actual")}
	source.instantiatedMemberSource = nil
	if c.pendingInstantiatedTable(source, nil) != nil {
		t.Fatal("tables not keyed by symbol names must stay eager")
	}
}

func TestPendingMembersDuplicateNameAndInheritanceMaterialization(t *testing.T) {
	c := pendingTestChecker()
	first := c.newSymbol(ast.SymbolFlagsProperty, "same")
	last := c.newSymbol(ast.SymbolFlagsProperty, "same")
	p := c.pendingInstantiatedList([]*ast.Symbol{first, last}, nil)
	selected := p.ownMember("same")
	if c.valueSymbolLinks.Get(selected).target != last {
		t.Fatal("duplicate-name lookup must use the last source entry")
	}
	before := c.SymbolCount
	table := p.ownTable()
	if table["same"] != selected || c.SymbolCount != before+1 {
		t.Fatal("materialization must preserve the last symbol and instantiate the earlier duplicate separately")
	}
	inherited := c.newSymbol(ast.SymbolFlagsProperty, "inherited")
	baseOverride := c.newSymbol(ast.SymbolFlagsProperty, "same")
	p.hasBases, p.resolving = true, true
	p.bases = []inheritedPendingMembers{{properties: []*ast.Symbol{inherited, baseOverride}}}
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	properties := typ.AsStructuredType().Properties()
	if len(properties) != 1 || properties[0] != selected {
		t.Fatal("reentrant properties must expose own members until bases finish")
	}
	members := typ.AsStructuredType().Members()
	if members["inherited"] != inherited || members["same"] != selected {
		t.Fatal("base materialization lost inheritance or overwrote an own value")
	}
	c.setStructuredTypeMembers(typ, members, nil, nil, nil)
	if len(typ.AsStructuredType().Properties()) != 2 {
		t.Fatal("completed resolution must expose inherited properties")
	}
}

func TestPendingOptionalQueriesDoNotInstantiateMembers(t *testing.T) {
	c := pendingTestChecker()
	symbol := c.newSymbol(ast.SymbolFlagsProperty|ast.SymbolFlagsOptional, "value")
	p := c.pendingInstantiatedList([]*ast.Symbol{symbol}, nil)
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	before := c.SymbolCount
	if !hasResolvedProperties(typ.AsStructuredType()) || !resolvedPropertiesAreOptional(typ.AsStructuredType()) {
		t.Fatal("incorrect optional-member query")
	}
	if c.SymbolCount != before || typ.AsStructuredType().pendingMembers != p {
		t.Fatal("optional query eagerly instantiated symbols")
	}
}
