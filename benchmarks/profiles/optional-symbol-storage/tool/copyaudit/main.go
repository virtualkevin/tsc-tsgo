package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/types"
	"golang.org/x/tools/go/packages"
	"os"
	"sort"
)

type Site struct {
	File       string
	Line       int
	Expression string
	Parent     string
	Text       string
}

func symbolValue(t types.Type) bool {
	n, ok := t.(*types.Named)
	return ok && n.Obj().Pkg() != nil && n.Obj().Pkg().Path() == "github.com/microsoft/typescript-go/internal/ast" && n.Obj().Name() == "Symbol"
}
func main() {
	cfg := &packages.Config{Mode: packages.NeedName | packages.NeedFiles | packages.NeedCompiledGoFiles | packages.NeedImports | packages.NeedDeps | packages.NeedTypes | packages.NeedSyntax | packages.NeedTypesInfo, Tests: true}
	pkgs, err := packages.Load(cfg, "./...")
	if err != nil {
		panic(err)
	}
	if packages.PrintErrors(pkgs) > 0 {
		panic("package errors")
	}
	seen := map[string]bool{}
	sites := []Site{}
	for _, p := range pkgs {
		for _, f := range p.Syntax {
			file := p.Fset.Position(f.Pos()).Filename
			if seen[file] {
				continue
			}
			seen[file] = true
			data, err := os.ReadFile(file)
			if err != nil {
				panic(err)
			}
			tf := p.Fset.File(f.Pos())
			var stack []ast.Node
			ast.Inspect(f, func(n ast.Node) bool {
				if n == nil {
					stack = stack[:len(stack)-1]
					return false
				}
				var parent ast.Node
				if len(stack) > 0 {
					parent = stack[len(stack)-1]
				}
				stack = append(stack, n)
				e, ok := n.(ast.Expr)
				if !ok {
					return true
				}
				tv, ok := p.TypesInfo.Types[e]
				if !ok || !tv.IsValue() || !symbolValue(tv.Type) {
					return true
				}
				sites = append(sites, Site{file, p.Fset.Position(e.Pos()).Line, fmt.Sprintf("%T", e), fmt.Sprintf("%T", parent), string(data[tf.Offset(e.Pos()):tf.Offset(e.End())])})
				return true
			})
		}
	}
	sort.Slice(sites, func(i, j int) bool {
		if sites[i].File != sites[j].File {
			return sites[i].File < sites[j].File
		}
		return sites[i].Line < sites[j].Line
	})
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(sites); err != nil {
		panic(err)
	}
}
