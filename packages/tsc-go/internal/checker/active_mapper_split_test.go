package checker

import (
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
)

func TestActiveMapperSplitCachesKeepNestedPopulation(t *testing.T) {
	for _, aliased := range []bool{false, true} {
		name := "plain"
		if aliased {
			name = "alias"
		}
		t.Run(name, func(t *testing.T) {
			c := activeMapperTestChecker()
			outer := c.newTypeParameter(nil)
			first, second := c.newTypeParameter(nil), c.newTypeParameter(nil)
			firstTarget := c.newIntrinsicType(TypeFlagsString, "string")
			secondTarget := c.newIntrinsicType(TypeFlagsNumber, "number")
			var alias *TypeAlias
			if aliased {
				alias = &TypeAlias{symbol: &ast.Symbol{}, typeArguments: []*Type{first}}
			}
			var mapper *TypeMapper
			// First's request starts with no map. Its worker grows the active
			// stack, then Second's request creates that same mapper's map.
			// First must reuse that map after recursion rather than discard it.
			const depth = 24
			mappers := make([]*TypeMapper, depth)
			for i := depth - 1; i >= 0; i-- {
				index := i
				mappers[i] = newFunctionTypeMapper(func(input *Type) *Type {
					if index+1 == len(mappers) {
						return c.instantiateTypeWithAlias(second, mapper, alias)
					}
					return c.instantiateType(input, mappers[index+1])
				})
			}
			firstCalls, secondCalls := 0, 0
			mapper = newFunctionTypeMapper(func(input *Type) *Type {
				switch input {
				case first:
					firstCalls++
					if c.instantiateType(first, mappers[0]) != secondTarget {
						t.Fatal("recursive lookup lost Second's target")
					}
					return firstTarget
				case second:
					secondCalls++
					return secondTarget
				default:
					for range 2 {
						if c.instantiateTypeWithAlias(first, mapper, alias) != firstTarget || c.instantiateTypeWithAlias(second, mapper, alias) != secondTarget {
							t.Fatal("distinct inputs lost their targets")
						}
					}
					return firstTarget
				}
			})
			for range 2 {
				c.instantiateType(outer, mapper)
			}
			if firstCalls != 2 || secondCalls != 2 {
				t.Fatalf("two activations called workers %d/%d times, want 2/2", firstCalls, secondCalls)
			}
			if len(c.activeMappers) != 0 || len(c.activeTypeMappersCaches) != 0 || c.instantiationDepth != 0 {
				t.Fatal("recursive work left active state behind")
			}
		})
	}
}

func TestActiveMapperSplitCachesSeparateAliasesAndInvalidateBoth(t *testing.T) {
	c := activeMapperTestChecker()
	outer, inner := c.newTypeParameter(nil), c.newTypeParameter(nil)
	first := c.newIntrinsicType(TypeFlagsString, "string")
	second := c.newIntrinsicType(TypeFlagsNumber, "number")
	alias := &TypeAlias{symbol: &ast.Symbol{}}
	target, calls := first, 0
	var mapper *TypeMapper
	mapper = newFunctionTypeMapper(func(input *Type) *Type {
		if input == inner {
			calls++
			return target
		}
		if c.instantiateType(inner, mapper) != first {
			t.Fatal("plain request did not return its initial target")
		}
		target = second
		if c.instantiateTypeWithAlias(inner, mapper, alias) != second {
			t.Fatal("alias request incorrectly reused plain request")
		}
		if c.instantiateType(inner, mapper) != first || c.instantiateTypeWithAlias(inner, mapper, alias) != second {
			t.Fatal("plain and aliased cache entries were not independent")
		}
		c.clearActiveMapperCaches()
		if c.instantiateType(inner, mapper) != second {
			t.Fatal("invalidation retained the old plain target")
		}
		target = first
		if c.instantiateTypeWithAlias(inner, mapper, alias) != first {
			t.Fatal("invalidation retained the old alias target")
		}
		return first
	})
	c.instantiateType(outer, mapper)
	if calls != 4 {
		t.Fatalf("worker called %d times, want 4", calls)
	}
}

func TestActiveMapperSplitCachesClearDuringNestedWorker(t *testing.T) {
	for _, aliased := range []bool{false, true} {
		name := "plain"
		if aliased {
			name = "alias"
		}
		t.Run(name, func(t *testing.T) {
			c := activeMapperTestChecker()
			outer := c.newTypeParameter(nil)
			first, second := c.newTypeParameter(nil), c.newTypeParameter(nil)
			oldTarget := c.newIntrinsicType(TypeFlagsString, "string")
			newTarget := c.newIntrinsicType(TypeFlagsNumber, "number")
			var alias *TypeAlias
			if aliased {
				alias = &TypeAlias{symbol: &ast.Symbol{}}
			}
			target, firstCalls, secondCalls := oldTarget, 0, 0
			var mapper *TypeMapper
			mapper = newFunctionTypeMapper(func(input *Type) *Type {
				switch input {
				case first:
					firstCalls++
					target = newTarget
					c.clearActiveMapperCaches()
					return c.instantiateTypeWithAlias(second, mapper, alias)
				case second:
					secondCalls++
					return target
				default:
					if c.instantiateTypeWithAlias(second, mapper, alias) != oldTarget {
						t.Fatal("could not seed the old target")
					}
					for range 2 {
						if c.instantiateTypeWithAlias(first, mapper, alias) != newTarget || c.instantiateTypeWithAlias(second, mapper, alias) != newTarget {
							t.Fatal("clearing during a worker lost the new cached targets")
						}
					}
					return newTarget
				}
			})
			c.instantiateType(outer, mapper)
			if firstCalls != 1 || secondCalls != 2 {
				t.Fatalf("workers called %d/%d times, want 1/2", firstCalls, secondCalls)
			}
		})
	}
}
