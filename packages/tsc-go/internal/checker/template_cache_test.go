package checker

import (
	"fmt"
	"slices"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/parser"
)

func templateCacheTestChecker() *Checker {
	c := &Checker{
		stringLiteralTypes:   make(map[string]*Type),
		templateLiteralTypes: make(map[CacheHashKey]*Type),
		unionTypes:           make(map[CacheHashKey]*Type),
		unionOfUnionTypes:    make(map[UnionOfUnionKey]*Type),
	}
	c.stringType = c.newIntrinsicType(TypeFlagsString, "string")
	c.neverType = c.newIntrinsicType(TypeFlagsNever, "never")
	c.errorType = c.newIntrinsicType(TypeFlagsAny, "error")
	c.wildcardType = c.newIntrinsicType(TypeFlagsAny, "any")
	return c
}

func templateCacheTestUnion(c *Checker, values ...string) *Type {
	types := make([]*Type, len(values))
	for i, value := range values {
		types[i] = c.getStringLiteralType(value)
	}
	slices.SortFunc(types, CompareTypes)
	return c.newUnionType(ObjectFlagsPrimitiveUnion, types)
}

func templateCacheTestValues(t *testing.T, typ *Type, want ...string) {
	t.Helper()
	types := []*Type{typ}
	if typ.flags&TypeFlagsUnion != 0 {
		types = typ.Types()
	}
	var got []string
	for _, typ := range types {
		if typ.flags != TypeFlagsStringLiteral {
			t.Fatalf("expected string literals, got flags %v", typ.flags)
		}
		got = append(got, typ.AsLiteralType().value.(string))
	}
	slices.Sort(got)
	slices.Sort(want)
	if !slices.Equal(got, want) {
		t.Fatalf("template values = %q, want %q", got, want)
	}
}

func TestTemplateCachesKeepCompleteInputs(t *testing.T) {
	c := templateCacheTestChecker()
	values := templateCacheTestUnion(c, "x", "y")
	left := c.newTemplateLiteralType([]string{"a\x00", "b"}, []*Type{c.stringType})
	right := c.newTemplateLiteralType([]string{"a", "\x00b"}, []*Type{c.stringType})
	first := c.instantiateTemplateLiteralType(left, []*Type{values})
	templateCacheTestValues(t, first, "a\x00xb", "a\x00yb")
	for i := 0; i < 3; i++ {
		if got := c.instantiateTemplateLiteralType(left, []*Type{values}); got != first {
			t.Fatal("repeated instantiation changed identity")
		}
		if got := c.getTemplateLiteralType(left.AsTemplateLiteralType().texts, []*Type{values}); got != first {
			t.Fatal("distribution and instantiation disagree")
		}
	}
	second := c.instantiateTemplateLiteralType(right, []*Type{values})
	templateCacheTestValues(t, second, "ax\x00b", "ay\x00b")
	if first == second {
		t.Fatal("cache lost text-span boundaries or template identity")
	}
	replacement := templateCacheTestUnion(c, "z", "w")
	templateCacheTestValues(t, c.instantiateTemplateLiteralType(left, []*Type{replacement}), "a\x00zb", "a\x00wb")
	// Both argument positions participate in a distributed cross product.
	pair := c.newTemplateLiteralType([]string{"", "/", ""}, []*Type{c.stringType, c.stringType})
	templateCacheTestValues(t, c.instantiateTemplateLiteralType(pair, []*Type{values, replacement}), "x/z", "x/w", "y/z", "y/w")
	templateCacheTestValues(t, c.instantiateTemplateLiteralType(pair, []*Type{replacement, values}), "z/x", "z/y", "w/x", "w/y")
}

func TestTemplateCachesReportOversizedProductsAtEveryUse(t *testing.T) {
	for _, instantiate := range []bool{false, true} {
		t.Run(fmt.Sprintf("instantiate=%v", instantiate), func(t *testing.T) {
			c := templateCacheTestChecker()
			file := parser.ParseSourceFile(ast.SourceFileParseOptions{FileName: "/templates.ts", Path: "/templates.ts"}, "type First = string;\ntype Second = string;\n", core.ScriptKindTS)
			values := make([]string, 50)
			for i := range values {
				values[i] = fmt.Sprint(i)
			}
			union := templateCacheTestUnion(c, values...)
			args := []*Type{union, union, union} // 125,000 constituents exceeds the limit.
			texts := []string{"", "-", "-", ""}
			template := c.newTemplateLiteralType(texts, []*Type{c.stringType, c.stringType, c.stringType})
			for _, statement := range file.Statements.Nodes {
				c.currentNode = statement.Name()
				var result *Type
				if instantiate {
					result = c.instantiateTemplateLiteralType(template, args)
				} else {
					result = c.getTemplateLiteralType(texts, args)
				}
				if result != c.errorType {
					t.Fatal("oversized product did not return the error type")
				}
			}
			diagnostics := c.diagnostics.GetDiagnosticsForFile(file.FileName())
			if len(diagnostics) != 2 {
				t.Fatalf("reported %d errors for two use sites, want 2", len(diagnostics))
			}
			for _, diagnostic := range diagnostics {
				if diagnostic.Code() != 2590 {
					t.Fatalf("unexpected diagnostic %d", diagnostic.Code())
				}
			}
			if diagnostics[0].Pos() == diagnostics[1].Pos() {
				t.Fatal("distinct use sites lost diagnostic positions")
			}
		})
	}
}
