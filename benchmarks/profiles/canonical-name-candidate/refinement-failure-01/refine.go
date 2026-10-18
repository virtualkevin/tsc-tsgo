// Refine staged name boundaries using the candidate's actual Go types.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/constant"
	"go/format"
	"go/token"
	"go/types"
	"golang.org/x/tools/go/ast/astutil"
	"golang.org/x/tools/go/packages"
	"os"
	"path/filepath"
	"sort"
	"strconv"
)

const astPkg = "github.com/microsoft/typescript-go/internal/ast"

var queries = map[string]int{"getPropertyOfType": 1, "getPropertyOfTypeEx": 1, "getPropertyOfObjectType": 1, "getPropertyOfUnionOrIntersectionType": 1, "getUnionOrIntersectionProperty": 1, "createUnionOrIntersectionProperty": 1, "getResolvedMember": 1, "getTypeOfPropertyOfType": 1, "getSymbol": 1, "newSymbol": 1, "newSymbolEx": 1, "Resolve": 1, "lookup": 1, "lookupName": 0, "getExportOfModule": 1, "resolveExportByName": 1, "resolveName": 1}

func nodeType(t types.Type) bool {
	p, ok := t.(*types.Pointer)
	if !ok {
		return false
	}
	n, ok := p.Elem().(*types.Named)
	return ok && n.Obj().Name() == "Node" && n.Obj().Pkg().Path() == astPkg
}
func main() {
	out, err := filepath.Abs(os.Args[1])
	if err != nil {
		panic(err)
	}
	stage := filepath.Join(out, "staged")
	cwd, _ := os.Getwd()
	raw, err := os.ReadFile(filepath.Join(out, "overlay.json"))
	if err != nil {
		panic(err)
	}
	var overlay struct{ Replace map[string]string }
	if err = json.Unmarshal(raw, &overlay); err != nil {
		panic(err)
	}
	contents := map[string][]byte{}
	for k, v := range overlay.Replace {
		data, e := os.ReadFile(v)
		if e != nil {
			panic(e)
		}
		contents[k] = data
	}
	fs := token.NewFileSet()
	ps, err := packages.Load(&packages.Config{Fset: fs, Overlay: contents, Mode: packages.NeedName | packages.NeedFiles | packages.NeedCompiledGoFiles | packages.NeedSyntax | packages.NeedTypes | packages.NeedTypesInfo | packages.NeedImports | packages.NeedDeps}, "./...")
	if err != nil {
		panic(err)
	}
	if packages.PrintErrors(ps) != 0 {
		panic("candidate type checking failed before refinement")
	}
	pool := map[string]string{}
	count := 0
	for _, p := range ps {
		info := p.TypesInfo
		qualify := func(name string) ast.Expr {
			if p.PkgPath == astPkg {
				return ast.NewIdent(name)
			}
			return &ast.SelectorExpr{X: ast.NewIdent("ast"), Sel: ast.NewIdent(name)}
		}
		key := func(e ast.Expr) ast.Expr {
			if tv, ok := info.Types[e]; ok && tv.Value != nil && tv.Value.Kind() == constant.String {
				text := constant.StringVal(tv.Value)
				if text == "" {
					return &ast.CompositeLit{Type: qualify("Name")}
				}
				hash := sha256.Sum256([]byte(text))
				name := "CanonicalName" + hex.EncodeToString(hash[:6])
				pool[text] = name
				return &ast.CallExpr{Fun: qualify(name)}
			}
			if call, ok := e.(*ast.CallExpr); ok && len(call.Args) == 0 {
				if sel, ok := call.Fun.(*ast.SelectorExpr); ok && sel.Sel.Name == "Text" && nodeType(info.TypeOf(sel.X)) {
					return &ast.CallExpr{Fun: &ast.SelectorExpr{X: sel.X, Sel: ast.NewIdent("NameKey")}}
				}
			}
			return nil
		}
		for _, f := range p.Syntax {
			changed := false
			astutil.Apply(f, nil, func(c *astutil.Cursor) bool {
				call, ok := c.Node().(*ast.CallExpr)
				if !ok {
					return true
				}
				var obj types.Object
				var name string
				var selection *types.Selection
				switch fun := call.Fun.(type) {
				case *ast.Ident:
					obj = info.Uses[fun]
					name = fun.Name
				case *ast.SelectorExpr:
					selection = info.Selections[fun]
					if selection != nil {
						obj = selection.Obj()
					} else {
						obj = info.Uses[fun.Sel]
					}
					name = fun.Sel.Name
				}
				if obj == nil || obj.Pkg() == nil {
					return true
				}
				if obj.Pkg().Path() == astPkg && name == "MakeName" && len(call.Args) == 1 {
					if replacement := key(call.Args[0]); replacement != nil {
						c.Replace(replacement)
						changed = true
						count++
					}
					return true
				}
				index, ok := queries[name]
				if !ok || index >= len(call.Args) {
					return true
				}
				if obj.Pkg().Path() != "github.com/microsoft/typescript-go/internal/checker" && obj.Pkg().Path() != "github.com/microsoft/typescript-go/internal/binder" {
					return true
				}
				// Only rewrite a call with a real carried-name counterpart.
				var target types.Object
				if selection != nil {
					target, _, _ = types.LookupFieldOrMethod(selection.Recv(), true, obj.Pkg(), name+"Key")
				} else {
					target = obj.Pkg().Scope().Lookup(name + "Key")
				}
				if target == nil {
					return true
				}
				if replacement := key(call.Args[index]); replacement != nil {
					call.Args[index] = replacement
					switch fun := call.Fun.(type) {
					case *ast.Ident:
						fun.Name += "Key"
					case *ast.SelectorExpr:
						fun.Sel.Name += "Key"
					}
					changed = true
					count++
				}
				return true
			})
			if changed {
				file := fs.Position(f.Pos()).Filename
				rel, e := filepath.Rel(cwd, file)
				if e != nil {
					panic(e)
				}
				target := filepath.Join(stage, rel)
				var data bytes.Buffer
				if e = format.Node(&data, fs, f); e != nil {
					panic(e)
				}
				if e = os.MkdirAll(filepath.Dir(target), 0755); e != nil {
					panic(e)
				}
				if e = os.WriteFile(target, data.Bytes(), 0644); e != nil {
					panic(e)
				}
			}
		}
	}
	texts := make([]string, 0, len(pool))
	for text := range pool {
		texts = append(texts, text)
	}
	sort.Strings(texts)
	var generated bytes.Buffer
	generated.WriteString("// Code generated by canonical-name-candidate/refine.go; DO NOT EDIT.\npackage ast\n\n")
	for _, text := range texts {
		name := pool[text]
		fmt.Fprintf(&generated, "var cached%s = MakeName(%s)\n// %s returns the canonical key for %s.\nfunc %s() Name { return cached%s }\n\n", name, strconv.Quote(text), name, strconv.Quote(text), name, name)
	}
	data, e := format.Source(generated.Bytes())
	if e != nil {
		panic(e)
	}
	if e = os.WriteFile(filepath.Join(stage, "internal/ast/canonical_names_generated.go"), data, 0644); e != nil {
		panic(e)
	}
	fmt.Printf("refined %d call sites; %d cached constant names\n", count, len(pool))
}
