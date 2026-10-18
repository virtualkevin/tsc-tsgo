// Add carried-name entry points and route stored names/recursive calls to them.
// Operates only on staged source. String wrappers preserve existing callers.
package main

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"golang.org/x/tools/go/ast/astutil"
	"os"
	"path/filepath"
	"strings"
)

var selected = map[string]int{"getPropertyOfType": 1, "getPropertyOfTypeEx": 1, "getPropertyOfObjectType": 1, "getPropertyOfUnionOrIntersectionType": 1, "getUnionOrIntersectionProperty": 1, "createUnionOrIntersectionProperty": 1, "getResolvedMember": 1, "getTypeOfPropertyOfType": 1, "getSymbol": 1, "newSymbol": 1, "newSymbolEx": 1}

func render(fs *token.FileSet, n ast.Node) string {
	var b bytes.Buffer
	if err := format.Node(&b, fs, n); err != nil {
		panic(err)
	}
	return b.String()
}
func main() {
	root, err := filepath.Abs(os.Args[1])
	if err != nil {
		panic(err)
	}
	fs := token.NewFileSet()
	files := map[string]*ast.File{}
	err = filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if !d.IsDir() && strings.HasSuffix(path, ".go") {
			f, e := parser.ParseFile(fs, path, nil, parser.ParseComments)
			if e != nil {
				return e
			}
			files[path] = f
		}
		return nil
	})
	if err != nil {
		panic(err)
	}
	for path, f := range files {
		changed := false
		var added []ast.Decl
		for _, decl := range f.Decls {
			fn, ok := decl.(*ast.FuncDecl)
			if !ok || fn.Body == nil {
				continue
			}
			old := fn.Name.Name
			index, carry := selected[old]
			var param string
			var wrapper *ast.FuncDecl
			if carry {
				// Selected names belong to binder/checker; do not transform unrelated APIs.
				if !strings.Contains(path, "/internal/checker/") && !strings.Contains(path, "/internal/binder/") {
					carry = false
				}
			}
			if carry {
				var params []*ast.Ident
				for _, field := range fn.Type.Params.List {
					params = append(params, field.Names...)
				}
				param = params[index].Name
				parsed, e := parser.ParseFile(token.NewFileSet(), "wrapper.go", "package p\n"+render(fs, fn), 0)
				if e != nil {
					panic(e)
				}
				wrapper = parsed.Decls[0].(*ast.FuncDecl)
				var target ast.Expr = ast.NewIdent(old + "Key")
				if fn.Recv != nil {
					target = &ast.SelectorExpr{X: ast.NewIdent(fn.Recv.List[0].Names[0].Name), Sel: ast.NewIdent(old + "Key")}
				}
				args := make([]ast.Expr, len(params))
				for i, p := range params {
					args[i] = ast.NewIdent(p.Name)
				}
				args[index] = &ast.CallExpr{Fun: &ast.SelectorExpr{X: ast.NewIdent("ast"), Sel: ast.NewIdent("MakeName")}, Args: []ast.Expr{args[index]}}
				wrapper.Body = &ast.BlockStmt{List: []ast.Stmt{&ast.ReturnStmt{Results: []ast.Expr{&ast.CallExpr{Fun: target, Args: args}}}}}
				wrapper.Doc = nil
			}
			astutil.Apply(fn.Body, nil, func(c *astutil.Cursor) bool {
				call, ok := c.Node().(*ast.CallExpr)
				if !ok {
					return true
				}
				var callName string
				switch fun := call.Fun.(type) {
				case *ast.Ident:
					callName = fun.Name
				case *ast.SelectorExpr:
					callName = fun.Sel.Name
				}
				if carry && callName == "MakeName" && len(call.Args) == 1 {
					if id, ok := call.Args[0].(*ast.Ident); ok && id.Name == param {
						c.Replace(ast.NewIdent("nameKey"))
						changed = true
						return true
					}
				}
				argIndex, ok := selected[callName]
				if !ok || argIndex >= len(call.Args) {
					return true
				}
				arg := call.Args[argIndex]
				var key ast.Expr
				if id, ok := arg.(*ast.Ident); ok && carry && id.Name == param {
					key = ast.NewIdent("nameKey")
				}
				if decode, ok := arg.(*ast.CallExpr); ok && len(decode.Args) == 0 {
					if sel, ok := decode.Fun.(*ast.SelectorExpr); ok && sel.Sel.Name == "String" {
						if field, ok := sel.X.(*ast.SelectorExpr); ok && (field.Sel.Name == "Name" || field.Sel.Name == "Text") {
							key = sel.X
						}
					}
				}
				if key != nil {
					call.Args[argIndex] = key
					switch fun := call.Fun.(type) {
					case *ast.Ident:
						fun.Name += "Key"
					case *ast.SelectorExpr:
						fun.Sel.Name += "Key"
					}
					changed = true
				}
				return true
			})
			if carry {
				fn.Name = ast.NewIdent(old + "Key")
				for _, field := range fn.Type.Params.List {
					for _, id := range field.Names {
						if id.Name == param {
							if len(field.Names) != 1 {
								panic("grouped parameter")
							}
							id.Name = "nameKey"
							field.Type = &ast.SelectorExpr{X: ast.NewIdent("ast"), Sel: ast.NewIdent("Name")}
						}
					}
				}
				used := false
				astutil.Apply(fn.Body, func(c *astutil.Cursor) bool {
					if id, ok := c.Node().(*ast.Ident); ok && id.Name == param {
						if sel, ok := c.Parent().(*ast.SelectorExpr); !ok || sel.Sel != id {
							used = true
						}
					}
					return true
				}, nil)
				if used {
					binding := &ast.AssignStmt{Lhs: []ast.Expr{ast.NewIdent(param)}, Tok: token.DEFINE, Rhs: []ast.Expr{&ast.CallExpr{Fun: &ast.SelectorExpr{X: ast.NewIdent("nameKey"), Sel: ast.NewIdent("String")}}}}
					fn.Body.List = append([]ast.Stmt{binding}, fn.Body.List...)
				}
				added = append(added, wrapper)
				changed = true
				fmt.Println(filepath.Base(path), old, "->", old+"Key")
			}
		}
		if changed {
			f.Decls = append(f.Decls, added...)
			if err := os.WriteFile(path, []byte(render(fs, f)), 0644); err != nil {
				panic(err)
			}
		}
	}
}
