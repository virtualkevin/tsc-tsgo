package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"reflect"
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

func TestPropertyViewTypeIndependentHistories(t *testing.T) {
	for seed := uint32(1); seed <= 64; seed++ {
		run := func(views bool) []int {
			c, owner, original, _ := viewFixture()
			parameter := c.newTypeParameter(nil)
			c.missingType = &Type{flags: TypeFlagsUndefined}
			c.neverType = &Type{flags: TypeFlagsNever}
			c.exactOptionalPropertyTypes = true
			c.valueSymbolLinks.Get(original).resolvedType = parameter
			calls := 0
			owner.pendingMembers.mapper = newFunctionTypeMapper(func(*Type) *Type { calls++; return c.missingType })
			v, _ := lookupPendingPropertyView(owner, "clone")
			var trace []int
			state := seed
			for i := 0; i < 24; i++ {
				state = state*1664525 + 1013904223
				op := state % 6
				switch op {
				case 0, 1:
					var got *Type
					if views {
						got = v.typeOf(c, op == 1)
					} else if op == 1 {
						got = c.getWriteTypeOfSymbol(getResolvedMember(owner, "clone"))
					} else {
						got = c.getTypeOfSymbol(getResolvedMember(owner, "clone"))
					}
					switch got {
					case c.missingType:
						trace = append(trace, 1)
					case c.neverType:
						trace = append(trace, 2)
					default:
						t.Fatal("unexpected result")
					}
				case 2:
					owner.Properties()
				case 3:
					owner.Members()
				case 4:
					c.clearActiveMapperCaches()
				case 5:
					runtime.GC()
				}
				trace = append(trace, calls, int(c.TotalInstantiationCount), int(c.instantiationDepth), len(c.activeMappers))
			}
			symbol := getResolvedMember(owner, "clone")
			trace = append(trace, int(c.SymbolCount))
			if symbol == original || getResolvedMember(owner, "clone") != symbol {
				t.Fatal("identity")
			}
			return trace
		}
		if a, b := run(false), run(true); !reflect.DeepEqual(a, b) {
			t.Fatalf("seed %d: %v != %v", seed, a, b)
		}
	}
}

func TestPropertyViewNestedQueryAssignment(t *testing.T) {
	for _, materialize := range []bool{false, true} {
		run := func(views bool) []int {
			c, owner, original, _ := viewFixture()
			parameter := c.newTypeParameter(nil)
			outer := &Type{flags: TypeFlagsString}
			inner := &Type{flags: TypeFlagsNumber}
			c.valueSymbolLinks.Get(original).resolvedType = parameter
			var trace []int
			calls := 0
			v, _ := lookupPendingPropertyView(owner, "clone")
			query := func() *Type {
				if views {
					return v.typeOf(c, false)
				}
				return c.getTypeOfSymbol(getResolvedMember(owner, "clone"))
			}
			owner.pendingMembers.mapper = newFunctionTypeMapper(func(*Type) *Type {
				calls++
				trace = append(trace, calls)
				if calls == 1 {
					if materialize {
						owner.Properties()
						owner.Members()
					}
					if query() != inner {
						t.Fatal("inner assignment")
					}
					return outer
				}
				return inner
			})
			if query() != outer || query() != outer {
				t.Fatal("outer assignment")
			}
			symbol := getResolvedMember(owner, "clone")
			if c.getTypeOfSymbol(symbol) != outer {
				t.Fatal("transfer")
			}
			trace = append(trace, int(c.TotalInstantiationCount), int(c.instantiationDepth), len(c.activeMappers), int(c.SymbolCount))
			return trace
		}
		if a, b := run(false), run(true); !reflect.DeepEqual(a, b) {
			t.Fatalf("materialize=%v: %v != %v", materialize, a, b)
		}
	}
}

func TestPropertyViewPanicHistory(t *testing.T) {
	run := func(views bool) []int {
		c, owner, original, _ := viewFixture()
		parameter := c.newTypeParameter(nil)
		c.valueSymbolLinks.Get(original).resolvedType = parameter
		calls := 0
		owner.pendingMembers.mapper = newFunctionTypeMapper(func(*Type) *Type { calls++; panic("mapper failure") })
		v, _ := lookupPendingPropertyView(owner, "clone")
		func() {
			defer func() {
				if recover() != "mapper failure" {
					t.Fatal("panic observation")
				}
			}()
			if views {
				v.typeOf(c, false)
			} else {
				c.getTypeOfSymbol(getResolvedMember(owner, "clone"))
			}
		}()
		// Compare the original failure residue; do not invent cleanup the old path lacks.
		symbol := getResolvedMember(owner, "clone")
		if c.valueSymbolLinks.Get(symbol).resolvedType != nil {
			t.Fatal("failed result cached")
		}
		return []int{calls, int(c.TotalInstantiationCount), int(c.instantiationDepth), len(c.activeMappers), int(c.SymbolCount)}
	}
	if a, b := run(false), run(true); !reflect.DeepEqual(a, b) {
		t.Fatalf("%v != %v", a, b)
	}
}

func TestPropertyViewRelationDifferential(t *testing.T) {
	for _, anyTarget := range []bool{false, true} {
		for _, optionalTarget := range []bool{false, true} {
			run := func(views bool) []int {
				c, owner, original, _ := viewFixture()
				typ := &Type{flags: TypeFlagsString}
				c.valueSymbolLinks.Get(original).resolvedType = typ
				target := c.newSymbol(ast.SymbolFlagsProperty, "clone")
				if optionalTarget {
					target.Flags |= ast.SymbolFlagsOptional
				}
				if anyTarget {
					c.valueSymbolLinks.Get(target).resolvedType = &Type{flags: TypeFlagsAny}
				} else {
					c.valueSymbolLinks.Get(target).resolvedType = typ
				}
				r := &Relater{c: c, relation: &Relation{}}
				v, _ := lookupPendingPropertyView(owner, "clone")
				var result Ternary
				before := c.SymbolCount
				if views {
					var supported bool
					result, supported = r.propertyViewRelatedTo(v, target, false, IntersectionStateNone)
					if !supported || c.SymbolCount != before {
						t.Fatal("unsupported or materialized")
					}
				} else {
					result = r.propertyRelatedTo(nil, nil, v.materialize(), target, c.getNonMissingTypeOfSymbol, false, IntersectionStateNone, false)
				}
				symbol := v.materialize()
				cache := 0
				if c.valueSymbolLinks.Get(symbol).resolvedType != nil {
					cache = 1
				}
				return []int{int(result), cache, int(c.SymbolCount), int(c.TotalInstantiationCount)}
			}
			if a, b := run(false), run(true); !reflect.DeepEqual(a, b) {
				t.Fatalf("any=%v optional=%v: %v != %v", anyTarget, optionalTarget, a, b)
			}
		}
	}
}

func TestPropertyViewRelationFallbackBeforeQueries(t *testing.T) {
	for _, mode := range []string{"diagnostic", "strict", "protected", "kept"} {
		c, owner, _, _ := viewFixture()
		target := c.newSymbol(ast.SymbolFlagsProperty, "clone")
		r := &Relater{c: c, relation: &Relation{}}
		name := "clone"
		if mode == "strict" {
			c.strictSubtypeRelation = r.relation
		}
		if mode == "protected" {
			target.CheckFlags = ast.CheckFlagsSyntheticProperty
		}
		if mode == "kept" {
			name = "kept"
		}
		v, _ := lookupPendingPropertyView(owner, name)
		before := c.SymbolCount
		if _, supported := r.propertyViewRelatedTo(v, target, mode == "diagnostic", IntersectionStateNone); supported {
			t.Fatal("accepted", mode)
		}
		if c.SymbolCount != before || len(owner.pendingMembers.viewTypes) != 0 || len(owner.pendingMembers.instantiated) != 0 {
			t.Fatal("fallback effects", mode)
		}
	}
}
