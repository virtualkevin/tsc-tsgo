package checker

import (
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/parser"
)

func activeMapperTestChecker() *Checker {
	c := &Checker{}
	c.couldContainTypeVariables = c.couldContainTypeVariablesWorker
	return c
}

func TestActiveMapperCacheLifetime(t *testing.T) {
	c := activeMapperTestChecker()
	outer, inner := c.newTypeParameter(nil), c.newTypeParameter(nil)
	first := c.newIntrinsicType(TypeFlagsString, "string")
	second := c.newIntrinsicType(TypeFlagsNumber, "number")
	target, calls := first, 0
	var mapper *TypeMapper
	mapper = newFunctionTypeMapper(func(input *Type) *Type {
		if input == inner {
			calls++
			return target
		}
		left := c.instantiateType(inner, mapper)
		right := c.instantiateType(inner, mapper)
		if left != right {
			t.Fatal("repeated active instantiation changed identity")
		}
		return left
	})
	if got := c.instantiateType(outer, mapper); got != first || calls != 1 {
		t.Fatalf("first activation = %p, calls %d; want %p, 1", got, calls, first)
	}
	target = second
	if got := c.instantiateType(outer, mapper); got != second || calls != 2 {
		t.Fatalf("second activation reused a stale result: %p, calls %d", got, calls)
	}
	if len(c.activeMappers) != 0 || len(c.activeTypeMappersCaches) != 0 || c.instantiationDepth != 0 {
		t.Fatal("outer instantiation left active state behind")
	}
	if c.TotalInstantiationCount != 4 || c.instantiationCount != 4 {
		t.Fatalf("instantiation counters = %d, %d; want 4, 4", c.TotalInstantiationCount, c.instantiationCount)
	}
}

func TestActiveMapperCacheInvalidation(t *testing.T) {
	c := activeMapperTestChecker()
	outer, inner := c.newTypeParameter(nil), c.newTypeParameter(nil)
	first := c.newIntrinsicType(TypeFlagsString, "string")
	second := c.newIntrinsicType(TypeFlagsNumber, "number")
	target, calls := first, 0
	var mapper *TypeMapper
	mapper = newFunctionTypeMapper(func(input *Type) *Type {
		if input == inner {
			calls++
			return target
		}
		if got := c.instantiateType(inner, mapper); got != first {
			t.Fatal("initial inference target was not returned")
		}
		target = second
		// Inference calls this after a target becomes known. The mapper is
		// still active, so its next use must observe the resolved target.
		c.clearActiveMapperCaches()
		got := c.instantiateType(inner, mapper)
		if c.instantiateType(inner, mapper) != got {
			t.Fatal("resolved target did not retain its identity")
		}
		return got
	})
	if got := c.instantiateType(outer, mapper); got != second || calls != 2 {
		t.Fatalf("invalidation returned %p with %d calls; want %p and 2", got, calls, second)
	}
}

func TestActiveMapperCacheSurvivesNestedMapperGrowth(t *testing.T) {
	c := activeMapperTestChecker()
	outer, inner := c.newTypeParameter(nil), c.newTypeParameter(nil)
	target := c.newIntrinsicType(TypeFlagsString, "string")
	// The nested activation stack outgrows the initial backing arrays while
	// the outer mapper's cache is being populated.
	const depth = 24
	mappers := make([]*TypeMapper, depth)
	for i := depth - 1; i >= 0; i-- {
		index := i
		mappers[i] = newFunctionTypeMapper(func(input *Type) *Type {
			if index+1 == len(mappers) {
				return target
			}
			return c.instantiateType(input, mappers[index+1])
		})
	}
	calls := 0
	var mapper *TypeMapper
	mapper = newFunctionTypeMapper(func(input *Type) *Type {
		if input == inner {
			calls++
			return c.instantiateType(input, mappers[0])
		}
		first := c.instantiateType(inner, mapper)
		second := c.instantiateType(inner, mapper)
		if first != second {
			t.Fatal("nested activation discarded the outer cached result")
		}
		return second
	})
	if got := c.instantiateType(outer, mapper); got != target || calls != 1 {
		t.Fatalf("nested result = %p, worker calls %d; want %p, 1", got, calls, target)
	}
	if len(c.activeMappers) != 0 || len(c.activeTypeMappersCaches) != 0 || c.instantiationDepth != 0 {
		t.Fatal("nested activation did not restore active state")
	}
}

func TestActiveMapperCacheDistinguishesAliases(t *testing.T) {
	c := activeMapperTestChecker()
	outer, inner := c.newTypeParameter(nil), c.newTypeParameter(nil)
	first := c.newIntrinsicType(TypeFlagsString, "string")
	second := c.newIntrinsicType(TypeFlagsNumber, "number")
	symbol := &ast.Symbol{}
	aliases := []*TypeAlias{
		nil,
		{symbol: symbol},
		{symbol: symbol, typeArguments: []*Type{first}},
		{symbol: symbol, typeArguments: []*Type{second}},
		{symbol: &ast.Symbol{}, typeArguments: []*Type{first}},
	}
	calls := 0
	var mapper *TypeMapper
	mapper = newFunctionTypeMapper(func(input *Type) *Type {
		if input == inner {
			calls++
			return first
		}
		for _, alias := range aliases {
			for range 2 {
				if c.instantiateTypeWithAlias(inner, mapper, alias) != first {
					t.Fatal("alias instantiation changed the mapped target")
				}
			}
		}
		return first
	})
	c.instantiateType(outer, mapper)
	if calls != len(aliases) {
		t.Fatalf("alias keys produced %d worker calls, want %d", calls, len(aliases))
	}
}

func TestActiveMapperCachePreservesAliasSymbolIDOrder(t *testing.T) {
	for _, withArguments := range []bool{false, true} {
		name := "empty"
		if withArguments {
			name = "withArguments"
		}
		t.Run(name, func(t *testing.T) {
			c := activeMapperTestChecker()
			input := c.newTypeParameter(nil)
			target := c.newIntrinsicType(TypeFlagsString, "string")
			alias := &TypeAlias{symbol: &ast.Symbol{}}
			if withArguments {
				alias.typeArguments = []*Type{input}
			}
			marker := &ast.Symbol{}
			var markerID ast.SymbolId
			mapper := newFunctionTypeMapper(func(*Type) *Type {
				markerID = ast.GetSymbolId(marker)
				return target
			})
			if c.instantiateTypeWithAlias(input, mapper, alias) != target {
				t.Fatal("new mapper returned the wrong target")
			}
			// GetSymbolId is lazy. Assigning the alias ID only after the worker
			// would reverse this ordering even though the unused hash is skipped.
			if aliasID := ast.GetSymbolId(alias.symbol); aliasID >= markerID {
				t.Fatalf("alias ID %d was not assigned before worker ID %d", aliasID, markerID)
			}
		})
	}
}

func TestActiveMapperCacheDoesNotBypassInstantiationLimits(t *testing.T) {
	for _, limit := range []string{"depth", "count"} {
		t.Run(limit, func(t *testing.T) {
			c := activeMapperTestChecker()
			input := c.newTypeParameter(nil)
			target := c.newIntrinsicType(TypeFlagsString, "string")
			c.errorType = c.newIntrinsicType(TypeFlagsAny, "error")
			mapper := newSimpleTypeMapper(input, target)
			c.pushActiveMapper(mapper)
			defer c.popActiveMapper()
			if c.instantiateType(input, mapper) != target {
				t.Fatal("could not prime active cache")
			}
			if limit == "depth" {
				c.instantiationDepth = 100
			} else {
				c.instantiationCount = 5_000_000
			}
			file := parser.ParseSourceFile(ast.SourceFileParseOptions{FileName: "/limits.ts", Path: "/limits.ts"}, "type First = string;\ntype Second = string;\n", core.ScriptKindTS)
			for _, statement := range file.Statements.Nodes {
				c.currentNode = statement.Name()
				if c.instantiateType(input, mapper) != c.errorType {
					t.Fatal("cache hit bypassed the instantiation limit")
				}
			}
			diagnostics := c.diagnostics.GetDiagnosticsForFile(file.FileName())
			if len(diagnostics) != 2 {
				t.Fatalf("got %d diagnostics for two use sites, want 2", len(diagnostics))
			}
			if diagnostics[0].Code() != 2589 || diagnostics[1].Code() != 2589 || diagnostics[0].Pos() == diagnostics[1].Pos() {
				t.Fatal("instantiation-limit diagnostics lost their codes or distinct positions")
			}
			if c.TotalInstantiationCount != 1 {
				t.Fatalf("limited requests changed instantiation count to %d", c.TotalInstantiationCount)
			}
		})
	}
}
