package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"reflect"
	"testing"
)

type directLoopObservation struct {
	Calls    []int
	Values   []int
	Reuses   bool
	Nil      bool
	Capacity int
	Count    uint32
}

// Compare real instantiation effects, identity relationships and backing-slice
// reuse against the unchanged generic implementation on independent checkers.
func TestDirectInstantiationTypeHistories(t *testing.T) {
	for _, size := range []int{0, 1, 2, 8, 64} {
		for change := -1; change < size; change++ {
			for _, mutate := range []bool{false, true} {
				run := func(direct bool) directLoopObservation {
					c := activeMapperTestChecker()
					inputs := make([]*Type, size, size+3)
					for i := range inputs {
						inputs[i] = c.newTypeParameter(nil)
					}
					originals := append([]*Type(nil), inputs...)
					target := c.newIntrinsicType(TypeFlagsString, "string")
					o := directLoopObservation{}
					m := newFunctionTypeMapper(func(v *Type) *Type {
						index := -1
						for i, p := range originals {
							if p == v {
								index = i
								break
							}
						}
						o.Calls = append(o.Calls, index)
						// A callback can mutate later input elements. Preserve live reads, and
						// preserve copying the prefix only after the first changed result.
						if mutate && index == 0 && size > 1 {
							inputs[size-1] = originals[0]
						}
						if index == change {
							return target
						}
						return v
					})
					var got []*Type
					if direct {
						got = c.instantiateTypes(inputs, m)
					} else {
						got = instantiateList(c, inputs, m, (*Checker).instantiateType)
					}
					o.Nil = got == nil
					o.Capacity = cap(got)
					o.Reuses = len(got) == 0 || &got[0] == &inputs[0]
					o.Count = c.TotalInstantiationCount
					for _, v := range got {
						id := -1
						if v == target {
							id = -2
						} else {
							for i, p := range originals {
								if p == v {
									id = i
									break
								}
							}
						}
						o.Values = append(o.Values, id)
					}
					if c.instantiationDepth != 0 || len(c.activeMappers) != 0 {
						t.Fatal("unbalanced instantiation state")
					}
					return o
				}
				a, b := run(false), run(true)
				if !reflect.DeepEqual(a, b) {
					t.Fatalf("size=%d change=%d mutate=%v: %#v != %#v", size, change, mutate, a, b)
				}
			}
		}
	}
	c := activeMapperTestChecker()
	if c.instantiateTypes(nil, nil) != nil {
		t.Fatal("nil input changed")
	}
}

func TestDirectInstantiationIndexHistories(t *testing.T) {
	for _, change := range []int{-1, 0, 1, 7} {
		run := func(direct bool) directLoopObservation {
			c := activeMapperTestChecker()
			parameter := c.newTypeParameter(nil)
			fixed := c.newIntrinsicType(TypeFlagsString, "string")
			target := c.newIntrinsicType(TypeFlagsNumber, "number")
			inputs := make([]*IndexInfo, 8, 11)
			for i := range inputs {
				value := fixed
				if i == change {
					value = parameter
				}
				inputs[i] = c.newIndexInfo(fixed, value, i%2 == 0, nil, nil)
			}
			m := newSimpleTypeMapper(parameter, target)
			var got []*IndexInfo
			if direct {
				got = c.instantiateIndexInfos(inputs, m)
			} else {
				got = instantiateList(c, inputs, m, (*Checker).instantiateIndexInfo)
			}
			o := directLoopObservation{Capacity: cap(got), Reuses: &got[0] == &inputs[0], Count: c.TotalInstantiationCount}
			for i, v := range got {
				same := 0
				if v == inputs[i] {
					same = 1
				}
				o.Values = append(o.Values, same)
				if v.keyType != fixed || v.isReadonly != (i%2 == 0) || v.valueType != map[bool]*Type{true: target, false: fixed}[i == change] {
					t.Fatal("index payload changed")
				}
			}
			return o
		}
		if a, b := run(false), run(true); !reflect.DeepEqual(a, b) {
			t.Fatalf("change=%d: %#v != %#v", change, a, b)
		}
	}
}

func TestDirectInstantiationSymbolHistories(t *testing.T) {
	for _, change := range []int{-1, 0, 1, 7} {
		run := func(direct bool) directLoopObservation {
			c := lazyPropertyTestChecker()
			parameter := c.newTypeParameter(nil)
			inputs := make([]*ast.Symbol, 8, 11)
			for i := range inputs {
				value := c.stringType
				if i == change {
					value = parameter
				}
				inputs[i] = lazyProperty(c, "p", value, false)
			}
			m := newSimpleTypeMapper(parameter, c.numberType)
			before := c.SymbolCount
			var got []*ast.Symbol
			if direct {
				got = c.instantiateSymbols(inputs, m)
			} else {
				got = instantiateList(c, inputs, m, (*Checker).instantiateSymbol)
			}
			o := directLoopObservation{Capacity: cap(got), Reuses: &got[0] == &inputs[0], Count: c.SymbolCount - before}
			for i, v := range got {
				same := 0
				if v == inputs[i] {
					same = 1
				}
				o.Values = append(o.Values, same)
				want := c.stringType
				if i == change {
					want = c.numberType
				}
				if c.getTypeOfSymbol(v) != want {
					t.Fatal("symbol type changed")
				}
			}
			return o
		}
		if a, b := run(false), run(true); !reflect.DeepEqual(a, b) {
			t.Fatalf("change=%d: %#v != %#v", change, a, b)
		}
	}
	c := activeMapperTestChecker()
	if c.instantiateSymbols(nil, nil) != nil {
		t.Fatal("nil input changed")
	}
	x := []*ast.Symbol{nil, nil}
	if y := c.instantiateSymbols(x, nil); &y[0] != &x[0] {
		t.Fatal("nil symbols did not reuse input")
	}
}

func TestDirectInstantiationSignatureHistories(t *testing.T) {
	for _, size := range []int{0, 1, 8} {
		run := func(direct bool) directLoopObservation {
			c := lazyPropertyTestChecker()
			parameter := c.newTypeParameter(nil)
			m := newSimpleTypeMapper(parameter, c.numberType)
			inputs := make([]*Signature, size, size+3)
			for i := range inputs {
				arg := lazyProperty(c, "arg", parameter, false)
				inputs[i] = c.newSignature(0, nil, nil, nil, []*ast.Symbol{arg}, parameter, nil, 1)
			}
			before := c.SymbolCount
			var got []*Signature
			if direct {
				got = c.instantiateSignatures(inputs, m)
			} else {
				got = instantiateList(c, inputs, m, (*Checker).instantiateSignature)
			}
			o := directLoopObservation{Capacity: cap(got), Count: c.SymbolCount - before, Reuses: size == 0 || &got[0] == &inputs[0]}
			for i, v := range got {
				if v == inputs[i] || v.target != inputs[i] || v.mapper != m || v.resolvedReturnType != nil || len(v.parameters) != 1 || c.getTypeOfSymbol(v.parameters[0]) != c.numberType {
					t.Fatal("signature identity, laziness or payload changed")
				}
				o.Values = append(o.Values, int(v.minArgumentCount))
			}
			return o
		}
		if a, b := run(false), run(true); !reflect.DeepEqual(a, b) {
			t.Fatalf("size=%d: %#v != %#v", size, a, b)
		}
	}
}
