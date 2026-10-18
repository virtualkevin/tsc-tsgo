package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"path/filepath"
	"testing"
)

func primitivePropertyFixture(kind ast.Kind) *ast.Symbol {
	f := ast.NodeFactory{}
	d := f.NewPropertySignatureDeclaration(nil, f.NewIdentifier("p"), nil, f.NewToken(kind), nil)
	d.Parent = &ast.Node{Kind: ast.KindTypeLiteral}
	return &ast.Symbol{Flags: ast.SymbolFlagsProperty, ValueDeclaration: d, Declarations: []*ast.Node{d}}
}
func TestPrimitivePropertyKeywords(t *testing.T) {
	for _, k := range []ast.Kind{ast.KindAnyKeyword, ast.KindUnknownKeyword, ast.KindStringKeyword, ast.KindNumberKeyword, ast.KindBigIntKeyword, ast.KindBooleanKeyword, ast.KindSymbolKeyword, ast.KindObjectKeyword, ast.KindVoidKeyword, ast.KindUndefinedKeyword, ast.KindNeverKeyword} {
		s := primitivePropertyFixture(k)
		if got := primitivePropertyCategory(s); got != 7 {
			t.Fatalf("%v: %d", k, got)
		}
		s.Flags |= ast.SymbolFlagsOptional
		if primitivePropertyCategory(s) != 7 {
			t.Fatal("optional property excluded")
		}
	}
}
func TestPrimitivePropertyExclusions(t *testing.T) {
	cases := []struct {
		name string
		edit func(*ast.Symbol)
		want int
	}{
		{"accessor", func(s *ast.Symbol) { s.Flags |= ast.SymbolFlagsSetAccessor }, 0},
		{"transient", func(s *ast.Symbol) { s.Flags |= ast.SymbolFlagsTransient }, 0},
		{"synthetic", func(s *ast.Symbol) { s.CheckFlags = ast.CheckFlagsSyntheticProperty }, 1},
		{"merged", func(s *ast.Symbol) { s.Declarations = append(s.Declarations, s.ValueDeclaration) }, 2},
		{"missing-value", func(s *ast.Symbol) { s.ValueDeclaration = nil }, 2},
		{"class-parent", func(s *ast.Symbol) { s.ValueDeclaration.Parent = &ast.Node{Kind: ast.KindClassDeclaration} }, 3},
		{"missing-parent", func(s *ast.Symbol) { s.ValueDeclaration.Parent = nil }, 3},
		{"javascript", func(s *ast.Symbol) { s.ValueDeclaration.Flags |= ast.NodeFlagsJavaScriptFile }, 4},
		{"no-type", func(s *ast.Symbol) { s.ValueDeclaration.AsPropertySignatureDeclaration().Type = nil }, 5},
		{"initializer", func(s *ast.Symbol) {
			s.ValueDeclaration.AsPropertySignatureDeclaration().Initializer = &ast.Node{Kind: ast.KindNumericLiteral}
		}, 5},
		{"this", func(s *ast.Symbol) { s.ValueDeclaration.Type().Kind = ast.KindThisKeyword }, 6},
	}
	for _, x := range cases {
		s := primitivePropertyFixture(ast.KindStringKeyword)
		x.edit(s)
		if got := primitivePropertyCategory(s); got != x.want {
			t.Fatalf("%s: %d, want %d", x.name, got, x.want)
		}
	}
	if primitivePropertyCategory(nil) != 0 {
		t.Fatal("nil accepted")
	}
}
func TestPrimitivePropertyExclusiveOutput(t *testing.T) {
	p := filepath.Join(t.TempDir(), "census.json")
	if err := WritePrimitivePropertySnapshots(p, nil); err != nil {
		t.Fatal(err)
	}
	before, _ := os.ReadFile(p)
	if err := WritePrimitivePropertySnapshots(p, nil); err == nil {
		t.Fatal("overwrote evidence")
	}
	after, _ := os.ReadFile(p)
	if string(before) != string(after) {
		t.Fatal("changed evidence")
	}
}
