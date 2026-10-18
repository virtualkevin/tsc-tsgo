// One-shot type-directed migration of the retained map-based SymbolTable.
// Run from packages/tsc-go before installing the new table implementation.
package main

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/format"
	"go/token"
	"go/types"
	"os"
	"path/filepath"

	"golang.org/x/tools/go/ast/astutil"
	"golang.org/x/tools/go/packages"
)

func isTable(t types.Type) bool {
	if t == nil {
		return false
	}
	n, ok := types.Unalias(t).(*types.Named)
	return ok && n.Obj().Name() == "SymbolTable" && n.Obj().Pkg() != nil && n.Obj().Pkg().Path() == "github.com/microsoft/typescript-go/internal/ast"
}
func call(x ast.Expr, name string, args ...ast.Expr) *ast.CallExpr {
	return &ast.CallExpr{Fun: &ast.SelectorExpr{X: x, Sel: ast.NewIdent(name)}, Args: args}
}
func constructor(typ ast.Expr, name string, args ...ast.Expr) *ast.CallExpr {
	var fun ast.Expr = ast.NewIdent(name)
	if s, ok := typ.(*ast.SelectorExpr); ok {
		fun = &ast.SelectorExpr{X: s.X, Sel: ast.NewIdent(name)}
	}
	return &ast.CallExpr{Fun: fun, Args: args}
}
func main() {
	fs := token.NewFileSet()
	ps, err := packages.Load(&packages.Config{Fset: fs, Tests: true, Mode: packages.NeedName | packages.NeedFiles | packages.NeedCompiledGoFiles | packages.NeedSyntax | packages.NeedTypes | packages.NeedTypesInfo | packages.NeedImports | packages.NeedDeps}, "./...")
	if err != nil {
		panic(err)
	}
	if packages.PrintErrors(ps) != 0 {
		panic("initial type checking failed")
	}
	seen := map[string]bool{}
	cwd, _ := os.Getwd()
	changed := 0
	for _, p := range ps {
		for _, f := range p.Syntax {
			path := fs.Position(f.Pos()).Filename
			rel, _ := filepath.Rel(cwd, path)
			if seen[path] || filepath.IsAbs(rel) || len(rel) >= 3 && rel[:3] == "../" {
				continue
			}
			seen[path] = true
			tables := map[ast.Expr]bool{}
			ast.Inspect(f, func(n ast.Node) bool {
				if e, ok := n.(ast.Expr); ok {
					tables[e] = isTable(p.TypesInfo.TypeOf(e))
				}
				return true
			})
			modified := false
			astutil.Apply(f, nil, func(c *astutil.Cursor) bool {
				replace := func(n ast.Node) {
					if e, ok := n.(ast.Expr); ok {
						if old, ok := c.Node().(ast.Expr); ok && tables[old] {
							tables[e] = true
						}
					}
					c.Replace(n)
					modified = true
				}
				switch n := c.Node().(type) {
				case *ast.AssignStmt:
					for _, lhs := range n.Lhs {
						if idx, ok := lhs.(*ast.IndexExpr); ok && tables[idx.X] {
							if len(n.Lhs) != 1 || len(n.Rhs) != 1 || n.Tok != token.ASSIGN {
								panic(fmt.Sprintf("unsupported table assignment at %s", fs.Position(n.Pos())))
							}
							replace(&ast.ExprStmt{X: call(idx.X, "Set", idx.Index, n.Rhs[0])})
							break
						}
					}
				case *ast.IndexExpr:
					if !tables[n.X] {
						break
					}
					if a, ok := c.Parent().(*ast.AssignStmt); ok {
						isLHS := false
						for _, lhs := range a.Lhs {
							if lhs == n {
								isLHS = true
							}
						}
						if isLHS {
							break
						}
						if len(a.Lhs) == 2 && len(a.Rhs) == 1 {
							replace(call(n.X, "Get", n.Index))
							break
						}
					}
					replace(call(n.X, "Lookup", n.Index))
				case *ast.RangeStmt:
					if tables[n.X] {
						n.X = call(n.X, "All")
						modified = true
					}
				case *ast.CallExpr:
					if id, ok := n.Fun.(*ast.Ident); ok {
						if b, ok := p.TypesInfo.Uses[id].(*types.Builtin); ok {
							if b.Name() == "make" && len(n.Args) > 0 && tables[n.Args[0]] {
								args := n.Args[1:]
								if len(args) == 0 {
									args = []ast.Expr{&ast.BasicLit{Kind: token.INT, Value: "0"}}
								}
								replace(constructor(n.Args[0], "NewSymbolTable", args...))
								break
							}
							if len(n.Args) > 0 && tables[n.Args[0]] {
								switch b.Name() {
								case "len":
									replace(call(n.Args[0], "Len"))
								case "delete":
									replace(call(n.Args[0], "Delete", n.Args[1]))
								case "clear":
									replace(call(n.Args[0], "Clear"))
								}
							}
						}
					}
					if s, ok := n.Fun.(*ast.SelectorExpr); ok {
						if fn, ok := p.TypesInfo.Uses[s.Sel].(*types.Func); ok && fn.Pkg() != nil && fn.Pkg().Path() == "maps" && len(n.Args) == 1 && tables[n.Args[0]] {
							switch fn.Name() {
							case "Clone", "Values", "All":
								replace(call(n.Args[0], fn.Name()))
							default:
								panic("unsupported maps function: " + fn.Name())
							}
						}
					}
				case *ast.CompositeLit:
					if !tables[n] {
						break
					}
					if len(n.Elts) == 0 {
						replace(constructor(n.Type, "NewSymbolTable", &ast.BasicLit{Kind: token.INT, Value: "0"}))
						break
					}
					var symbol ast.Expr = ast.NewIdent("Symbol")
					if s, ok := n.Type.(*ast.SelectorExpr); ok {
						symbol = &ast.SelectorExpr{X: s.X, Sel: ast.NewIdent("Symbol")}
					}
					lit := &ast.CompositeLit{Type: &ast.MapType{Key: ast.NewIdent("string"), Value: &ast.StarExpr{X: symbol}}, Elts: n.Elts}
					replace(constructor(n.Type, "NewSymbolTableFromMap", lit))
				}
				return true
			})
			if !modified {
				continue
			}
			// Remove only imports made unused by this rewrite. Compiler checks follow.
			for _, imp := range append([]*ast.ImportSpec(nil), f.Imports...) {
				if imp.Path.Value == "\"maps\"" && !astutil.UsesImport(f, "maps") {
					astutil.DeleteImport(fs, f, "maps")
				}
			}
			var out bytes.Buffer
			if err := format.Node(&out, fs, f); err != nil {
				panic(err)
			}
			if err := os.WriteFile(path, out.Bytes(), 0644); err != nil {
				panic(err)
			}
			fmt.Println(rel)
			changed++
		}
	}
	fmt.Printf("changed files: %d\n", changed)
}
