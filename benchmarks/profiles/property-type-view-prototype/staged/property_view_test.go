package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"runtime"
	"testing"
)

func viewFixture() (*Checker, *StructuredType, *ast.Symbol, *ast.Symbol) {
	c := pendingTestChecker()
	clone := c.newSymbol(ast.SymbolFlagsProperty|ast.SymbolFlagsOptional, "clone")
	clone.CheckFlags = ast.CheckFlagsReadonly
	kept := c.newSymbol(ast.SymbolFlagsProperty, "kept")
	c.valueSymbolLinks.Get(kept).resolvedType = &Type{flags: TypeFlagsString}
	p := c.pendingInstantiatedList([]*ast.Symbol{clone, kept}, nil)
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
	return c, typ.AsStructuredType(), clone, kept
}
func TestPropertyViewMetadataAndIdentity(t *testing.T) {
	c, owner, original, kept := viewFixture()
	before := c.SymbolCount
	v, ok := lookupPendingPropertyView(owner, "clone")
	if !ok {
		t.Fatal("unsupported")
	}
	metadata := v.metadata()
	if c.SymbolCount != before || len(owner.pendingMembers.instantiated) != 0 {
		t.Fatal("metadata materialized")
	}
	symbol := v.materialize()
	if symbol == original || metadata != metadataOfProperty(symbol) || v.materialize() != symbol {
		t.Fatal("clone/identity/metadata")
	}
	k, ok := lookupPendingPropertyView(owner, "kept")
	if !ok || k.materialize() != kept {
		t.Fatal("keep")
	}
	missing, ok := lookupPendingPropertyView(owner, "absent")
	if !ok || missing.materialize() != nil {
		t.Fatal("missing")
	}
}
func TestPropertyViewFrozenDecisionAndRetirement(t *testing.T) {
	c, owner, original, _ := viewFixture()
	v, _ := lookupPendingPropertyView(owner, "clone")
	// Later source resolution cannot change the earlier decision to clone.
	c.valueSymbolLinks.Get(original).resolvedType = &Type{flags: TypeFlagsNumber}
	if v.kept {
		t.Fatal("setup")
	}
	expected := v.metadata()
	owner.Properties()
	symbol := v.materialize()
	if symbol == original || v.metadata() != expected {
		t.Fatal("frozen decision")
	}
	owner.Members()
	runtime.GC()
	runtime.GC()
	if v.materialize() != symbol || v.metadata() != metadataOfProperty(symbol) {
		t.Fatal("retired pending identity")
	}
	runtime.KeepAlive(v)
}
func TestPropertyViewFallbackBeforeEffects(t *testing.T) {
	for _, mode := range []string{"bases", "resolving", "duplicate", "instantiated"} {
		c, owner, original, _ := viewFixture()
		p := owner.pendingMembers
		switch mode {
		case "bases":
			p.hasBases = true
		case "resolving":
			p.resolving = true
		case "duplicate":
			p.source.entries = append(p.source.entries, original)
		case "instantiated":
			original.CheckFlags |= ast.CheckFlagsInstantiated
		}
		before := c.SymbolCount
		if _, ok := lookupPendingPropertyView(owner, "clone"); ok {
			t.Fatalf("accepted %s", mode)
		}
		if c.SymbolCount != before || len(p.instantiated) != 0 {
			t.Fatal("fallback effects")
		}
	}
}
func TestPropertyViewIndependentHistories(t *testing.T) {
	for _, enumerateFirst := range []bool{false, true} {
		run := func(views bool) ([]propertyViewMetadata, []bool, uint32) {
			c, owner, original, kept := viewFixture()
			var trace []propertyViewMetadata
			var identity []bool
			v, _ := lookupPendingPropertyView(owner, "clone")
			k, _ := lookupPendingPropertyView(owner, "kept")
			if enumerateFirst {
				owner.Properties()
			}
			var first *ast.Symbol
			if views {
				first = v.materialize()
			} else {
				first = getResolvedMember(owner, "clone")
			}
			trace = append(trace, metadataOfProperty(first))
			identity = append(identity, first == original)
			owner.Properties()
			owner.Members()
			runtime.GC()
			var again, other *ast.Symbol
			if views {
				again = v.materialize()
				other = k.materialize()
				trace = append(trace, v.metadata())
			} else {
				again = getResolvedMember(owner, "clone")
				other = getResolvedMember(owner, "kept")
				trace = append(trace, metadataOfProperty(again))
			}
			identity = append(identity, first == again, other == kept)
			return trace, identity, c.SymbolCount
		}
		a, b, countA := run(false)
		c, d, countB := run(true)
		if len(a) != len(c) || len(b) != len(d) || countA != countB {
			t.Fatal("history sizes/count")
		}
		for i := range a {
			if a[i] != c[i] {
				t.Fatal("metadata history")
			}
		}
		for i := range b {
			if b[i] != d[i] {
				t.Fatal("identity history")
			}
		}
	}
}

func TestPropertyViewTypeCacheTransfer(t *testing.T) {
	c, owner, original, _ := viewFixture()
	parameter := c.newTypeParameter(nil)
	result := &Type{flags: TypeFlagsString}
	c.valueSymbolLinks.Get(original).resolvedType = parameter
	calls := 0
	owner.pendingMembers.mapper = newFunctionTypeMapper(func(typ *Type) *Type {
		calls++
		if typ != parameter {
			t.Fatal("input")
		}
		return result
	})
	v, ok := lookupPendingPropertyView(owner, "clone")
	if !ok {
		t.Fatal("view")
	}
	before := c.SymbolCount
	if v.typeOf(c, false) != result || v.typeOf(c, false) != result || c.SymbolCount != before || calls != 1 {
		t.Fatal("deferred cache")
	}
	nameType := &Type{flags: TypeFlagsNumber}
	c.valueSymbolLinks.Get(original).nameType = nameType
	symbol := v.materialize()
	if c.getTypeOfSymbol(symbol) != result || calls != 1 || c.valueSymbolLinks.Get(symbol).nameType != nil {
		t.Fatal("cache/name snapshot transfer")
	}
	owner.Properties()
	owner.Members()
	runtime.GC()
	if v.typeOf(c, false) != result || v.materialize() != symbol {
		t.Fatal("retirement")
	}
}

func TestPropertyViewReentrantTypeMaterialization(t *testing.T) {
	for _, useView := range []bool{false, true} {
		c, owner, original, _ := viewFixture()
		parameter := c.newTypeParameter(nil)
		result := &Type{flags: TypeFlagsString}
		c.valueSymbolLinks.Get(original).resolvedType = parameter
		calls := 0
		var symbol *ast.Symbol
		owner.pendingMembers.mapper = newFunctionTypeMapper(func(typ *Type) *Type {
			calls++
			owner.Properties()
			owner.Members()
			runtime.GC()
			symbol = getResolvedMember(owner, "clone")
			return result
		})
		v, _ := lookupPendingPropertyView(owner, "clone")
		var got *Type
		if useView {
			got = v.typeOf(c, false)
		} else {
			got = c.getTypeOfSymbol(v.materialize())
		}
		if got != result || c.getTypeOfSymbol(symbol) != result || calls != 1 || c.instantiationDepth != 0 || c.TotalInstantiationCount != 1 {
			t.Fatal("reentrant history", useView, calls)
		}
	}
}
