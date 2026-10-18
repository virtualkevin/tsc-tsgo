package parser_test

import (
 "testing"
 "github.com/microsoft/typescript-go/internal/ast"
 "github.com/microsoft/typescript-go/internal/core"
 "github.com/microsoft/typescript-go/internal/parser"
 "github.com/microsoft/typescript-go/internal/tspath"
)

func TestCanonicalNameStorageFactory(t *testing.T) {
 clones := 0
 factory := ast.NewNodeFactory(ast.NodeFactoryHooks{OnClone: func(_, _ *ast.Node) { clones++ }})
 for _, text := range []string{"", "a", "\xfecall", "\x00\xff", "é"} {
  first := factory.NewIdentifier(text)
  second := factory.NewIdentifierName(first.NameKey())
  clone := first.Clone(factory)
  if first == second || first == clone || first.Text() != text || second.Text() != text || clone.Text() != text || first.NameKey() != second.NameKey() || first.NameKey() != clone.NameKey() {
   t.Fatalf("identifier factory/clone identity changed for %q", text)
  }
 }
 if clones != 5 || factory.TextCount() != 15 { t.Fatalf("factory accounting changed: clones=%d text=%d", clones, factory.TextCount()) }
 empty := factory.NewStringLiteral("", 0)
 if empty.Text() != "" || empty.NameKey() != (ast.Name{}) || empty.NameKey() == ast.MakeName(ast.InternalSymbolNameMissing) {
  t.Fatal("empty literal and missing-name sentinel conflated")
 }
}

func TestCanonicalNameStorageParser(t *testing.T) {
 parse := func(path, text string) *ast.SourceFile {
  return parser.ParseSourceFile(ast.SourceFileParseOptions{FileName:path, Path:tspath.Path(path)}, text, core.ScriptKindTS)
 }
 first := parse("/canonical-one.ts", `let \u0061 = 1; a; let \u{62} = a; b;`)
 second := parse("/canonical-two.ts", `let a = 2; a;`)
 if len(first.Diagnostics()) != 0 || len(second.Diagnostics()) != 0 { t.Fatal("fixture failed parsing") }
 expected := ast.MakeName("a")
 count := 0
 var visit func(*ast.Node) bool
 visit = func(node *ast.Node) bool {
  if node.Kind == ast.KindIdentifier && node.Text() == "a" {
   count++
   if node.NameKey() != expected || node.AsIdentifier().Text != expected { t.Fatal("parser lost canonical name") }
  }
  node.ForEachChild(visit)
  return false
 }
 first.AsNode().ForEachChild(visit)
 second.AsNode().ForEachChild(visit)
 if count != 5 { t.Fatalf("expected 5 decoded a identifiers, got %d", count) }
 for _, file := range []*ast.SourceFile{first, second} {
  if file.Identifiers["a"] != expected { t.Fatal("parser interner did not carry identifier handle") }
 }
 if first.Identifiers["b"] != ast.MakeName("b") { t.Fatal("escaped identifier name collection changed") }
}
