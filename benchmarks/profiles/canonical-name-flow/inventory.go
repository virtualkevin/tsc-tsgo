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
	Function   string `json:"function"`
	Origin     string `json:"origin"`
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

func named(t types.Type, name string) bool {
	if t == nil {
		return false
	}
	t = types.Unalias(t)
	if p, ok := t.(*types.Pointer); ok {
		t = types.Unalias(p.Elem())
	}
	n, ok := t.(*types.Named)
	return ok && n.Obj().Name() == name && n.Obj().Pkg() != nil && n.Obj().Pkg().Path() == "github.com/microsoft/typescript-go/internal/ast"
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
	cwd, err := os.Getwd()
	if err != nil {
		panic(err)
	}
	hashes := map[string]string{}
	counts := map[string]int{}
	var sites []Site
	for _, p := range ps {
		for _, f := range p.Syntax {
			file := fs.Position(f.Pos()).Filename
			rel, err := filepath.Rel(cwd, file)
			if err != nil || strings.HasPrefix(rel, "..") {
				panic("source outside module")
			}
			data, err := os.ReadFile(file)
			if err != nil {
				panic(err)
			}
			h := sha256.Sum256(data)
			hashes[rel] = hex.EncodeToString(h[:])
			parents := map[ast.Node]ast.Node{}
			params := map[types.Object]bool{}
			rangeKeys := map[types.Object]bool{}
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
				if fn, ok := n.(*ast.FuncType); ok && fn.Params != nil {
					for _, field := range fn.Params.List {
						for _, id := range field.Names {
							if o := p.TypesInfo.Defs[id]; o != nil {
								params[o] = true
							}
						}
					}
				}
				if r, ok := n.(*ast.RangeStmt); ok && symbolTable(p.TypesInfo.TypeOf(r.X)) {
					if id, ok := r.Key.(*ast.Ident); ok {
						if o := p.TypesInfo.Defs[id]; o != nil {
							rangeKeys[o] = true
						}
					}
				}
				return true
			})
			origin := func(e ast.Expr) string {
				if tv, ok := p.TypesInfo.Types[e]; ok && tv.Value != nil {
					return "constant"
				}
				switch x := e.(type) {
				case *ast.Ident:
					o := p.TypesInfo.Uses[x]
					if params[o] {
						return "parameter"
					}
					if rangeKeys[o] {
						return "symbol-table-range-key"
					}
					return "other-identifier"
				case *ast.SelectorExpr:
					if sel := p.TypesInfo.Selections[x]; sel != nil && x.Sel.Name == "Name" && named(sel.Recv(), "Symbol") {
						return "symbol-name-field"
					}
					if sel := p.TypesInfo.Selections[x]; sel != nil && x.Sel.Name == "Text" && named(sel.Recv(), "Identifier") {
						return "identifier-text-field"
					}
					return "other-selector"
				case *ast.CallExpr:
					return "call-result"
				case *ast.IndexExpr:
					return "index-result"
				case *ast.BinaryExpr:
					return "binary-expression"
				default:
					return fmt.Sprintf("%T", e)
				}
			}
			add := func(n ast.Node, op, org string) {
				pos := fs.Position(n.Pos())
				function := "<package>"
				for a := n; a != nil; a = parents[a] {
					if fn, ok := a.(*ast.FuncDecl); ok {
						function = fn.Name.Name
						break
					}
				}
				context := ""
				if parents[n] != nil {
					context = render(fs, parents[n])
					if len(context) > 1000 {
						context = context[:1000] + " [truncated]"
					}
				}
				sites = append(sites, Site{Function: function, Origin: org, File: rel, Line: pos.Line, Column: pos.Column, Operation: op, Expression: render(fs, n), Context: context})
				counts[op+":"+org]++
			}
			ast.Inspect(f, func(n ast.Node) bool {
				switch x := n.(type) {
				case *ast.IndexExpr:
					if symbolTable(p.TypesInfo.TypeOf(x.X)) {
						op := "table-read"
						if a, ok := parents[x].(*ast.AssignStmt); ok {
							for _, lhs := range a.Lhs {
								if lhs == x {
									op = "table-write"
								}
							}
						}
						add(x, op, origin(x.Index))
					}
				case *ast.SelectorExpr:
					sel := p.TypesInfo.Selections[x]
					if sel == nil {
						break
					}
					if sel.Kind() == types.FieldVal && ((x.Sel.Name == "Name" && named(sel.Recv(), "Symbol")) || (x.Sel.Name == "Text" && named(sel.Recv(), "Identifier"))) {
						op := "symbol-name-use"
						if x.Sel.Name == "Text" {
							op = "identifier-text-use"
						}
						add(x, op, fmt.Sprintf("%T", parents[x]))
					}
					if sel.Kind() == types.MethodVal && x.Sel.Name == "Text" && named(sel.Recv(), "Node") {
						add(x, "node-text-method", fmt.Sprintf("%T", parents[x]))
					}
				case *ast.KeyValueExpr:
					if lit, ok := parents[x].(*ast.CompositeLit); ok && named(p.TypesInfo.TypeOf(lit), "Symbol") {
						if key, ok := x.Key.(*ast.Ident); ok && key.Name == "Name" {
							add(x, "symbol-name-initializer", origin(x.Value))
						}
					}
				}
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
		return a.Operation < b.Operation
	})
	out := struct {
		Scope        string
		Packages     int
		SourceHashes map[string]string
		Counts       map[string]int
		Sites        []Site
	}{"Current-platform non-test typed source inventory. Direct syntactic key origins only; no interprocedural dataflow, dynamic frequency, eligible reuse, allocation or speedup claim. Node.Text includes non-identifier nodes. Field sites can overlap table sites. Other build configurations and tests excluded.", len(ps), hashes, counts, sites}
	b, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		panic(err)
	}
	fmt.Println(string(b))
}
