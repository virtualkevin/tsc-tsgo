// Run from packages/tsc-go with the pinned Go toolchain. This is an offline
// source inventory, not compiler instrumentation or a performance measurement.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/format"
	"go/token"
	"go/types"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"golang.org/x/tools/go/packages"
)

type Site struct {
	File       string `json:"file"`
	Line       int    `json:"line"`
	Column     int    `json:"column"`
	Operation  string `json:"operation"`
	Expression string `json:"expression"`
	Context    string `json:"context"`
}

func symbolTable(t types.Type) bool {
	if t == nil {
		return false
	}
	m, ok := t.Underlying().(*types.Map)
	if !ok || !types.Identical(m.Key(), types.Typ[types.String]) {
		return false
	}
	p, ok := m.Elem().(*types.Pointer)
	if !ok {
		return false
	}
	n, ok := p.Elem().(*types.Named)
	return ok && n.Obj().Name() == "Symbol" && n.Obj().Pkg() != nil && n.Obj().Pkg().Path() == "github.com/microsoft/typescript-go/internal/ast"
}

func render(fs *token.FileSet, n ast.Node) string {
	var b bytes.Buffer
	if err := format.Node(&b, fs, n); err != nil {
		panic(err)
	}
	return b.String()
}

func main() {
	fs := token.NewFileSet()
	ps, err := packages.Load(&packages.Config{Fset: fs, Mode: packages.NeedName | packages.NeedFiles | packages.NeedCompiledGoFiles | packages.NeedSyntax | packages.NeedTypes | packages.NeedTypesInfo | packages.NeedImports | packages.NeedDeps}, "./...")
	if err != nil {
		panic(err)
	}
	if packages.PrintErrors(ps) != 0 {
		panic("type checking failed")
	}
	var sites []Site
	hashes := map[string]string{}
	counts := map[string]int{}
	cwd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	for _, p := range ps {
		for _, f := range p.Syntax {
			file := fs.Position(f.Pos()).Filename
			rel, err := filepath.Rel(cwd, file)
			if err != nil {
				panic(err)
			}
			if strings.HasPrefix(rel, "..") {
				panic("source outside module")
			}
			data, err := os.ReadFile(file)
			if err != nil {
				panic(err)
			}
			h := sha256.Sum256(data)
			hashes[rel] = hex.EncodeToString(h[:])
			parents := map[ast.Node]ast.Node{}
			var stack []ast.Node
			ast.Inspect(f, func(n ast.Node) bool {
				if n == nil {
					stack = stack[:len(stack)-1]
					return true
				}
				if len(stack) > 0 {
					parents[n] = stack[len(stack)-1]
				}
				stack = append(stack, n)
				return true
			})
			ast.Inspect(f, func(n ast.Node) bool {
				e, ok := n.(ast.Expr)
				if !ok || !symbolTable(p.TypesInfo.TypeOf(e)) {
					return true
				}
				if id, ok := e.(*ast.Ident); ok && p.TypesInfo.Defs[id] != nil {
					return true
				}
				if sel, ok := parents[n].(*ast.SelectorExpr); ok && sel.Sel == e {
					// The selector expression, not its field/type name token, is the value.
					return true
				}
				// Type expressions are not runtime table values.
				if tv, ok := p.TypesInfo.Types[e]; ok && tv.IsType() {
					return true
				}
				parent := parents[n]
				if parent == nil {
					return true
				}
				op := "other-value-use"
				switch q := parent.(type) {
				case *ast.IndexExpr:
					if q.X == e {
						op = "lookup"
						if a, ok := parents[q].(*ast.AssignStmt); ok {
							for _, lhs := range a.Lhs {
								if lhs == q {
									op = "write"
									if a.Tok != token.ASSIGN {
										op = "read-modify-write"
									}
								}
							}
						}
					}
				case *ast.RangeStmt:
					if q.X == e {
						op = "range"
					}
				case *ast.CallExpr:
					op = "call-argument"
					if id, ok := q.Fun.(*ast.Ident); ok {
						if b, ok := p.TypesInfo.Uses[id].(*types.Builtin); ok {
							op = "builtin-" + b.Name()
						}
					}
					if sel, ok := q.Fun.(*ast.SelectorExpr); ok {
						if fn, ok := p.TypesInfo.Uses[sel.Sel].(*types.Func); ok && fn.Pkg() != nil {
							op = "call-" + fn.Pkg().Path() + "." + fn.Name()
						}
					}
				case *ast.AssignStmt:
					op = "assignment"
				case *ast.ValueSpec:
					op = "declaration-initializer"
				case *ast.ReturnStmt:
					op = "return"
				case *ast.BinaryExpr:
					op = "comparison-" + q.Op.String()
				case *ast.UnaryExpr:
					op = "unary-" + q.Op.String()
				case *ast.KeyValueExpr:
					op = "composite-field"
				case *ast.ParenExpr:
					op = "parenthesized"
				}
				pos := fs.Position(e.Pos())
				context := render(fs, parent)
				if len(context) > 1000 {
					context = context[:1000] + " [truncated]"
				}
				sites = append(sites, Site{rel, pos.Line, pos.Column, op, render(fs, e), context})
				counts[op]++
				return true
			})
		}
	}
	sort.Slice(sites, func(i, j int) bool {
		a, b := sites[i], sites[j]
		if a.File != b.File {
			return a.File < b.File
		}
		if a.Line != b.Line {
			return a.Line < b.Line
		}
		if a.Column != b.Column {
			return a.Column < b.Column
		}
		return a.Expression < b.Expression
	})
	out := struct {
		Scope        string            `json:"scope"`
		Packages     int               `json:"packages"`
		SourceHashes map[string]string `json:"sourceHashes"`
		Counts       map[string]int    `json:"counts"`
		Sites        []Site            `json:"sites"`
	}{"Type-checked runtime expressions with underlying map[string]*ast.Symbol in current-platform non-test module packages. Counts are syntactic sites, not dynamic operations, distinct tables, allocation budgets or speedup forecasts. Nested expressions can describe the same operation. Generic conversions and unsafe identity need separate review. Other platforms and tests are excluded.", len(ps), hashes, counts, sites}
	b, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		panic(err)
	}
	fmt.Println(string(b))
}
