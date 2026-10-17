package checker

import (
	"fmt"
	"runtime"
	"testing"
	"weak"

	"github.com/microsoft/typescript-go/internal/ast"
)

type valueSymbolLinksLifetimeProbe struct {
	original weak.Pointer[ast.Symbol]
	first    weak.Pointer[ast.Symbol]
	second   weak.Pointer[ast.Symbol]
	links    weak.Pointer[ValueSymbolLinks]
	typ      weak.Pointer[Type]
	typeID   TypeId
	value    string
}

//go:noinline
func populateValueSymbolLinksLifetime(c *Checker, count int) []valueSymbolLinksLifetimeProbe {
	probes := make([]valueSymbolLinksLifetimeProbe, 0, count)
	for i := range count {
		original := c.newSymbol(ast.SymbolFlagsProperty, fmt.Sprintf("member%d", i))
		parameter := c.newTypeParameter(nil)
		value := fmt.Sprintf("retained-type-%d", i)
		target := c.newLiteralType(TypeFlagsStringLiteral, value, nil)
		c.valueSymbolLinks.Get(original).resolvedType = parameter
		mapper := newSimpleTypeMapper(parameter, target)
		// This actual checker constructor invokes fresh valueSymbolLinks.New.
		// The two resulting symbols have the same visible fields but distinct
		// pointer identities and must never share a links allocation.
		first := c.newInstantiatedSymbol(original, mapper)
		second := c.newInstantiatedSymbol(original, mapper)
		if c.getTypeOfSymbol(first) != target || c.getTypeOfSymbol(second) != target {
			panic("lifetime fixture did not instantiate the expected literal type")
		}
		probes = append(probes, valueSymbolLinksLifetimeProbe{
			original: weak.Make(original), first: weak.Make(first), second: weak.Make(second),
			links: weak.Make(c.valueSymbolLinks.Get(first)), typ: weak.Make(target),
			typeID: target.id, value: value,
		})
	}
	// No symbol, links or type pointer escapes through this probe slice.
	// The checker is the only strong root of the populated graph.
	return probes
}

func TestValueSymbolLinksRetainInstantiatedGraphAcrossGC(t *testing.T) {
	c := lazyPropertyTestChecker()
	const count = 4096
	probes := populateValueSymbolLinksLifetime(c, count)
	// 12,288 symbols and link entries displace many symbol and link arena
	// chunks and force repeated table growth, including long-lived early slots.
	for range 3 {
		runtime.GC()
	}
	for i, probe := range probes {
		original, first, second := probe.original.Value(), probe.first.Value(), probe.second.Value()
		links, typ := probe.links.Value(), probe.typ.Value()
		if original == nil || first == nil || second == nil || links == nil || typ == nil {
			t.Fatalf("checker lost part of retained graph %d", i)
		}
		if first == second || first.Name != second.Name || first.Flags != second.Flags || first.CheckFlags != second.CheckFlags {
			t.Fatalf("fixture %d lost distinct equal-field instantiations", i)
		}
		if c.valueSymbolLinks.Get(first) != links || c.valueSymbolLinks.Get(second) == links || links.target != original {
			t.Fatalf("instantiated symbol %d lost link or target identity", i)
		}
		if c.getTypeOfSymbol(first) != typ || c.getTypeOfSymbol(second) != typ || typ.id != probe.typeID || typ.AsLiteralType().value != probe.value {
			t.Fatalf("actual checker lookup lost type identity or concrete tail for %d", i)
		}
		// Read through actual checker instantiation machinery after GC, not
		// solely the container: retained mapper/target must still be usable.
		third := c.newInstantiatedSymbol(original, links.mapper)
		if c.getTypeOfSymbol(third) != typ || c.valueSymbolLinks.Get(third) == links {
			t.Fatalf("retained mapper graph %d no longer instantiates correctly", i)
		}
	}
	runtime.KeepAlive(c)
}

//go:noinline
func publishedValueSymbolLinks(c *Checker) (*ast.Symbol, *ValueSymbolLinks) {
	symbol := c.newSymbol(ast.SymbolFlagsProperty, "published")
	links := c.valueSymbolLinks.Get(symbol)
	links.resolvedType = c.newLiteralType(TypeFlagsStringLiteral, "old-published-tail", nil)
	links.writeType = links.resolvedType
	links.nameType = links.resolvedType
	links.functionOrConstructorChecked = true
	return symbol, links
}

func TestValueSymbolLinksReplacementKeepsPublishedPointers(t *testing.T) {
	c := lazyPropertyTestChecker()
	symbol, oldLinks := publishedValueSymbolLinks(c)
	// Production New is used only for fresh instantiated symbols. Explicitly
	// test its existing overwrite behavior too: an already published links
	// pointer must remain valid when the key's current entry is replaced.
	current := c.valueSymbolLinks.New(symbol)
	if current == oldLinks || *current != (ValueSymbolLinks{}) {
		t.Fatal("replacement reused or failed to zero the links allocation")
	}
	current.resolvedType = c.newLiteralType(TypeFlagsStringLiteral, "new-published-tail", nil)
	populateValueSymbolLinksLifetime(c, 1024) // Drop every independent probe/root.
	for range 3 {
		runtime.GC()
	}
	if c.valueSymbolLinks.Get(symbol) != current || c.getTypeOfSymbol(symbol) != current.resolvedType || c.getTypeOfSymbol(symbol).AsLiteralType().value != "new-published-tail" {
		t.Fatal("checker lookup did not retain the replacement")
	}
	if oldLinks.resolvedType.AsLiteralType().value != "old-published-tail" || oldLinks.writeType != oldLinks.resolvedType || oldLinks.nameType != oldLinks.resolvedType || !oldLinks.functionOrConstructorChecked {
		t.Fatal("replacement/growth corrupted a previously published links pointer")
	}
	runtime.KeepAlive(c)
	runtime.KeepAlive(oldLinks)
}
