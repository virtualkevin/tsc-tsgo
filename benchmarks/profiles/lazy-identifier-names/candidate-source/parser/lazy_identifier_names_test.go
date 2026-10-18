package parser

import (
	"fmt"
	"maps"
	"strings"
	"sync"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/core"
)

func TestLazyIdentifierNamesReplay(t *testing.T) {
	cases := []struct {
		name, text string
		kind       core.ScriptKind
	}{
		{"empty.ts", "", core.ScriptKindTS},
		{"normal.ts", `const repeated = 1; const other = repeated; class C { #privateName = repeated; ["quoted"] = 1 }`, core.ScriptKindTS},
		{"escapes.ts", `const \u0061 = "value"; a; import { "string export" as escaped } from "pkg"; type X = import("other").Name;`, core.ScriptKindTS},
		{"speculation.ts", `const x = <T>(arg: T) => arg; const y = async (name) => name; const z = foo < bar > (baz); f<T<U>>(x);`, core.ScriptKindTS},
		{"recovery.ts", `class C { ["prop"](: Invalid; export const = error; f<Stray(another);`, core.ScriptKindTS},
		{"await.ts", `const await = 1; export {}; await p; for await (const v of xs) { v; }`, core.ScriptKindTS},
		{"jsx.tsx", `const x = <Component attr={name}><namespace.Tag data-x="v" /></Component>;`, core.ScriptKindTSX},
		{"jsdoc.js", `/** @template T @param {T} input @returns {T} */ function f(input) { return input } /** @typedef {{hidden: number}} Shape */`, core.ScriptKindJS},
		{"links.ts", `/** @see target @link Other */ const name = 1; /** @param {Unparsed} hidden */ function f() {}`, core.ScriptKindTS},
		{"json.json", `{"property": 1, "quoted\u0061": {"nested": null}}`, core.ScriptKindJSON},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			opts := ast.SourceFileParseOptions{FileName: "/" + tc.name}
			eager := parseSourceFileWithIdentifierNames(opts, tc.text, tc.kind, true)
			lazy := ParseSourceFile(opts, tc.text, tc.kind)
			snapshot := func(file *ast.SourceFile) string {
				var b strings.Builder
				var visit func(*ast.Node) bool
				visit = func(n *ast.Node) bool {
					fmt.Fprintf(&b, "%v:%v:%v;", n.Kind, n.Flags, n.Loc)
					if ast.IsIdentifier(n) || ast.IsPrivateIdentifier(n) || ast.IsStringLiteral(n) {
						fmt.Fprintf(&b, "%q;", n.Text())
					}
					n.ForEachChild(visit)
					return false
				}
				visit(file.AsNode())
				for _, group := range [][]*ast.Diagnostic{file.Diagnostics(), file.JSDiagnostics(), file.JSDocDiagnostics()} {
					for _, d := range group {
						fmt.Fprintf(&b, "D:%v:%v:%v:%v;", d.Loc(), d.Code(), d.MessageKey(), d.MessageArgs())
					}
				}
				fmt.Fprintf(&b, "counts:%d:%d:%d", file.NodeCount, file.TextCount, file.IdentifierCount)
				return b.String()
			}
			before := snapshot(lazy)
			if before != snapshot(eager) {
				t.Fatal("lazy initial parse differs from eager")
			}
			// Exercise pooled-parser reuse before triggering replay.
			ParseSourceFile(ast.SourceFileParseOptions{FileName: "/unrelated.ts"}, "const unrelated = 0", core.ScriptKindTS)
			clone := lazy.Clone(&ast.NodeFactory{}).AsSourceFile()
			want := eager.IdentifierNames()
			var wg sync.WaitGroup
			for i := 0; i < 16; i++ {
				wg.Go(func() {
					if !maps.Equal(lazy.IdentifierNames(), want) || !maps.Equal(clone.IdentifierNames(), want) {
						t.Error("replayed collision set differs")
					}
				})
			}
			wg.Wait()
			if before != snapshot(lazy) {
				t.Fatal("replay changed original AST or diagnostics")
			}
		})
	}
}
