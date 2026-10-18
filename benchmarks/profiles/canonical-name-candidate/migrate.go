// One-time typed storage migration, run against baseline from packages/tsc-go.
// Subsequent hot-path propagation and compiler fixes are reviewed edits.
package main

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/format"
	"go/token"
	"go/types"
	"golang.org/x/tools/go/ast/astutil"
	"golang.org/x/tools/go/packages"
	"os"
	"path/filepath"
)

const astPkg = "github.com/microsoft/typescript-go/internal/ast"

func named(t types.Type, name string) bool {
	if t == nil {
		return false
	}
	t = types.Unalias(t)
	if p, ok := t.(*types.Pointer); ok {
		t = types.Unalias(p.Elem())
	}
	n, ok := t.(*types.Named)
	return ok && n.Obj().Pkg() != nil && n.Obj().Pkg().Path() == astPkg && n.Obj().Name() == name
}
func main() {
	fs := token.NewFileSet()
	ps, err := packages.Load(&packages.Config{Fset: fs, Mode: packages.NeedName | packages.NeedFiles | packages.NeedCompiledGoFiles | packages.NeedSyntax | packages.NeedTypes | packages.NeedTypesInfo | packages.NeedImports | packages.NeedDeps}, "./...")
	if err != nil {
		panic(err)
	}
	if packages.PrintErrors(ps) != 0 {
		panic("baseline type checking failed")
	}
	cwd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	staging := filepath.Join(cwd, "../../benchmarks/profiles/canonical-name-candidate/staged")
	count := 0
	for _, p := range ps {
		info := p.TypesInfo
		field := func(e ast.Expr) bool {
			s, ok := e.(*ast.SelectorExpr)
			if !ok {
				return false
			}
			sel := info.Selections[s]
			return sel != nil && ((s.Sel.Name == "Name" && named(sel.Recv(), "Symbol")) || (s.Sel.Name == "Text" && named(sel.Recv(), "Identifier")))
		}
		ranges := map[types.Object]bool{}
		writes := map[ast.Expr]bool{}
		for _, f := range p.Syntax {
			ast.Inspect(f, func(n ast.Node) bool {
				if r, ok := n.(*ast.RangeStmt); ok && named(info.TypeOf(r.X), "SymbolTable") {
					if id, ok := r.Key.(*ast.Ident); ok {
						if obj := info.Defs[id]; obj != nil {
							ranges[obj] = true
						}
					}
				}
				if a, ok := n.(*ast.AssignStmt); ok {
					for _, lhs := range a.Lhs {
						if field(lhs) {
							writes[lhs] = true
						}
					}
				}
				return true
			})
		}
		for _, f := range p.Syntax {
			changed := false
			decoded := map[ast.Expr]ast.Expr{}
			ident := func(name string) ast.Expr {
				if p.PkgPath == astPkg {
					return ast.NewIdent(name)
				}
				return &ast.SelectorExpr{X: ast.NewIdent("ast"), Sel: ast.NewIdent(name)}
			}
			toName := func(e ast.Expr) ast.Expr {
				if original, ok := decoded[e]; ok {
					return original
				}
				if call, ok := e.(*ast.CallExpr); ok && len(call.Args) == 0 {
					if sel, ok := call.Fun.(*ast.SelectorExpr); ok && sel.Sel.Name == "Text" && named(info.TypeOf(sel.X), "Node") {
						return &ast.CallExpr{Fun: &ast.SelectorExpr{X: sel.X, Sel: ast.NewIdent("NameKey")}}
					}
				}
				return &ast.CallExpr{Fun: ident("MakeName"), Args: []ast.Expr{e}}
			}
			astutil.Apply(f, nil, func(cursor *astutil.Cursor) bool {
				n := cursor.Node()
				switch e := n.(type) {
				case *ast.SelectorExpr:
					if field(e) && !writes[e] {
						replacement := &ast.CallExpr{Fun: &ast.SelectorExpr{X: e, Sel: ast.NewIdent("String")}}
						decoded[replacement] = e
						cursor.Replace(replacement)
						changed = true
					}
				case *ast.Ident:
					if ranges[info.Uses[e]] {
						replacement := &ast.CallExpr{Fun: &ast.SelectorExpr{X: e, Sel: ast.NewIdent("String")}}
						decoded[replacement] = e
						cursor.Replace(replacement)
						changed = true
					}
				case *ast.IndexExpr:
					if named(info.TypeOf(e.X), "SymbolTable") {
						e.Index = toName(e.Index)
						changed = true
					}
				case *ast.CallExpr:
					if id, ok := e.Fun.(*ast.Ident); ok && id.Name == "delete" && len(e.Args) == 2 && named(info.TypeOf(e.Args[0]), "SymbolTable") {
						e.Args[1] = toName(e.Args[1])
						changed = true
					}
				case *ast.AssignStmt:
					if len(e.Lhs) == len(e.Rhs) {
						for i, lhs := range e.Lhs {
							if writes[lhs] {
								e.Rhs[i] = toName(e.Rhs[i])
								changed = true
							}
						}
					}
				case *ast.CompositeLit:
					for _, elt := range e.Elts {
						if kv, ok := elt.(*ast.KeyValueExpr); ok {
							if named(info.TypeOf(e), "SymbolTable") {
								kv.Key = toName(kv.Key)
								changed = true
							}
							if id, ok := kv.Key.(*ast.Ident); ok && ((id.Name == "Name" && named(info.TypeOf(e), "Symbol")) || (id.Name == "Text" && named(info.TypeOf(e), "Identifier"))) {
								kv.Value = toName(kv.Value)
								changed = true
							}
						}
					}
				}
				return true
			})
			if changed {
				var buf bytes.Buffer
				if err := format.Node(&buf, fs, f); err != nil {
					panic(err)
				}
				file := fs.Position(f.Pos()).Filename
				rel, err := filepath.Rel(cwd, file)
				if err != nil {
					panic(err)
				}
				target := filepath.Join(staging, rel)
				if err := os.MkdirAll(filepath.Dir(target), 0755); err != nil {
					panic(err)
				}
				if err := os.WriteFile(target, buf.Bytes(), 0644); err != nil {
					panic(err)
				}
				count++
				fmt.Println(rel)
			}
		}
	}
	fmt.Println("rewritten files", count)
}
