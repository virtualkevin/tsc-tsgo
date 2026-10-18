package binder

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/parser"
	"github.com/microsoft/typescript-go/internal/tspath"
	"strings"
	"testing"
)

func TestCanonicalNameDeclarationKeys(t *testing.T) {
	const path = "/canonical-declarations.ts"
	source := parser.ParseSourceFile(ast.SourceFileParseOptions{FileName: path, Path: tspath.Path(path)}, `
 interface Names { "": string; "01": number; 1: string; [-1]: boolean; ["computed"]: string; \u0064ecoded: number; }
 class A { #x = 1; }
 class B { #x = 2; }
 declare module "quoted" { export const x: number; }
 `, core.ScriptKindTS)
	if len(source.Diagnostics()) != 0 {
		t.Fatal("fixture parse failed")
	}
	BindSourceFile(source)
	b := Binder{}
	expected := []string{"", "01", "1", "-1", "computed", "decoded"}
	var properties []ast.Name
	var private []ast.Name
	var module ast.Name
	var visit func(*ast.Node) bool
	visit = func(node *ast.Node) bool {
		switch node.Kind {
		case ast.KindPropertySignature:
			key := b.getDeclarationNameKey(node)
			properties = append(properties, key)
 if node.Symbol() == nil || node.Symbol().Name != key { t.Fatal("bound property symbol does not retain declaration key") }
			if key.String() == "decoded" && key != node.Name().NameKey() {
				t.Fatal("identifier declaration lost stored key")
			}
		case ast.KindPropertyDeclaration:
			if ast.IsPrivateIdentifier(node.Name()) {
				private = append(private, b.getDeclarationNameKey(node))
			}
		case ast.KindModuleDeclaration:
			module = b.getDeclarationNameKey(node)
		}
		node.ForEachChild(visit)
		return false
	}
	source.AsNode().ForEachChild(visit)
	if len(properties) != len(expected) {
		t.Fatalf("wrong property count: %d", len(properties))
	}
	for i, key := range properties {
		if key != ast.MakeName(expected[i]) {
			t.Fatalf("property %d: %q", i, key.String())
		}
	}
	if properties[0] != (ast.Name{}) || properties[0] == ast.MakeName(ast.InternalSymbolNameMissing) {
		t.Fatal("empty property confused with missing")
	}
	if len(private) != 2 || private[0] == private[1] {
		t.Fatal("private names from separate classes merged")
	}
	for _, key := range private {
		if !strings.HasPrefix(key.String(), ast.InternalSymbolNamePrefix+"#") || !strings.HasSuffix(key.String(), "@#x") {
			t.Fatalf("private spelling changed: %q", key.String())
		}
	}
	if module.String() != "\"quoted\"" {
		t.Fatalf("ambient module quoting changed: %q", module.String())
	}
}
