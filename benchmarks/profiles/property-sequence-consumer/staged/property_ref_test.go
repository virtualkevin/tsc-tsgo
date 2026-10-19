package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"reflect"
	"runtime"
	"testing"
)

func TestPropertyViewDualRelationHistory(t *testing.T) {
	for _, anyTarget := range []bool{false, true} {
		for _, optionalSource := range []bool{false, true} {
			for _, reenter := range []bool{false, true} {
				run := func(views bool) []int {
					c := pendingTestChecker()
					var trace []int
					makeOwner := func(optional bool) (*StructuredType, *ast.Symbol) {
						symbol := c.newSymbol(ast.SymbolFlagsProperty, "p")
						if optional {
							symbol.Flags |= ast.SymbolFlagsOptional
						}
						typ := c.newObjectType(ObjectFlagsAnonymous, nil)
						c.setPendingStructuredTypeMembers(typ, c.pendingInstantiatedList([]*ast.Symbol{symbol}, nil), nil, nil, nil)
						c.valueSymbolLinks.Get(symbol).resolvedType = c.newTypeParameter(nil)
						return typ.AsStructuredType(), symbol
					}
					source, _ := makeOwner(optionalSource)
					target, _ := makeOwner(false)
					shared := &Type{flags: TypeFlagsString}
					source.pendingMembers.mapper = newFunctionTypeMapper(func(*Type) *Type { trace = append(trace, 1); return shared })
					target.pendingMembers.mapper = newFunctionTypeMapper(func(*Type) *Type {
						trace = append(trace, 2)
						if reenter {
							target.Properties()
							source.Properties()
							runtime.GC()
						}
						if anyTarget {
							return &Type{flags: TypeFlagsAny}
						}
						return shared
					})
					r := &Relater{c: c, relation: &Relation{}}
					var result Ternary
					if views {
						targetSequence, ok := c.pendingPropertySequence(target)
						if !ok {
							t.Fatal("target unsupported")
						}
						sourceView, _ := lookupPendingPropertyView(source, "p")
						sourceView.prepareTypeState(c)
						before := c.SymbolCount
						var supported bool
						result, supported = r.propertyRefsRelatedTo(propertyRef{view: sourceView}, propertyRef{view: targetSequence.at(0)}, false, IntersectionStateNone)
						if !supported || (!reenter && c.SymbolCount != before) {
							t.Fatal("unexpected fallback or allocation")
						}
					} else {
						targetSymbol := target.Properties()[0]
						sourceSymbol := getResolvedMember(source, "p")
						result = r.propertyRelatedTo(nil, nil, sourceSymbol, targetSymbol, c.getNonMissingTypeOfSymbol, false, IntersectionStateNone, false)
					}
					source.Properties()
					target.Properties()
					source.Members()
					target.Members()
					trace = append(trace, int(result), int(c.SymbolCount), int(c.TotalInstantiationCount), int(c.instantiationDepth))
					for _, owner := range []*StructuredType{source, target} {
						cached := 0
						if c.valueSymbolLinks.Get(getResolvedMember(owner, "p")).resolvedType != nil {
							cached = 1
						}
						trace = append(trace, cached)
					}
					return trace
				}
				if eager, lazy := run(false), run(true); !reflect.DeepEqual(eager, lazy) {
					t.Fatalf("any=%v optional=%v reenter=%v: %v != %v", anyTarget, optionalSource, reenter, eager, lazy)
				}
			}
		}
	}
}

func TestPropertyViewReferenceIdentity(t *testing.T) {
	c, owner, _, kept := viewFixture()
	sequence, _ := c.pendingPropertySequence(owner)
	for i := range sequence.originals {
		v := sequence.at(i)
		ref := propertyRef{view: v}
		before := c.SymbolCount
		if !samePropertyRef(ref, ref) || c.SymbolCount != before {
			t.Fatal("self identity allocated")
		}
		if v.name == "kept" && !samePropertyRef(ref, propertyRef{symbol: kept}) {
			t.Fatal("kept identity")
		}
		symbol := v.materialize()
		if !samePropertyRef(ref, propertyRef{symbol: symbol}) {
			t.Fatal("published identity")
		}
		owner.Properties()
		owner.Members()
		runtime.GC()
		if !samePropertyRef(ref, propertyRef{symbol: symbol}) {
			t.Fatal("retired identity")
		}
	}
}

func TestPropertyViewDualFallbackBeforeQueries(t *testing.T) {
	for _, mode := range []string{"diagnostic", "strict", "protected"} {
		c, owner, _, _ := viewFixture()
		sequence, _ := c.pendingPropertySequence(owner)
		target := c.newSymbol(ast.SymbolFlagsProperty, "clone")
		r := &Relater{c: c, relation: &Relation{}}
		if mode == "strict" {
			c.strictSubtypeRelation = r.relation
		}
		if mode == "protected" {
			target.CheckFlags = ast.CheckFlagsSyntheticProperty
		}
		before := c.SymbolCount
		if _, supported := r.propertyRefsRelatedTo(propertyRef{view: sequence.at(0)}, propertyRef{symbol: target}, mode == "diagnostic", IntersectionStateNone); supported {
			t.Fatal("accepted", mode)
		}
		if c.SymbolCount != before || c.TotalInstantiationCount != 0 || len(owner.pendingMembers.instantiated) != 0 {
			t.Fatal("fallback effects")
		}
	}
}
