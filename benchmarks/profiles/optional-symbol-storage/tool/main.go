package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/token"
	"go/types"
	"golang.org/x/tools/go/packages"
	"os"
	"sort"
)

const astPath = "github.com/microsoft/typescript-go/internal/ast"

func isSymbol(t types.Type) bool {
	if p, ok := t.(*types.Pointer); ok {
		t = p.Elem()
	}
	n, ok := t.(*types.Named)
	return ok && n.Obj().Pkg() != nil && n.Obj().Pkg().Path() == astPath && n.Obj().Name() == "Symbol"
}
func selected(s *ast.SelectorExpr, info *types.Info) bool {
	if s.Sel.Name != "Members" && s.Sel.Name != "Exports" && s.Sel.Name != "ExportSymbol" {
		return false
	}
	sel := info.Selections[s]
	return sel != nil && sel.Kind() == types.FieldVal && isSymbol(sel.Recv())
}

type Site struct {
	File   string
	Line   int
	Field  string
	Parent string
	Kind   string
}

type Edit struct {
	File       string
	Start, End int
	Text       string
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
	edits := []Edit{}
	sourceHashes := map[string]string{}
	names := map[string]string{"Members": "MembersTable", "Exports": "ExportsTable", "ExportSymbol": "ExportTarget"}
	for _, p := range pkgs {
		for _, f := range p.Syntax {
			file := p.Fset.Position(f.Pos()).Filename
			if seen[file] {
				continue
			}
			seen[file] = true
			original, err := os.ReadFile(file)
			if err != nil {
				panic(err)
			}
			tf := p.Fset.File(f.Pos())
			add := func(start, end token.Pos, text string) {
				edits = append(edits, Edit{file, tf.Offset(start), tf.Offset(end), text})
				sourceHashes[file] = fmt.Sprintf("%x", sha256.Sum256(original))
			}
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
				if sel, ok := n.(*ast.SelectorExpr); ok && selected(sel, p.TypesInfo) {
					kind := "read"
					if a, ok := parent.(*ast.AssignStmt); ok {
						for _, lhs := range a.Lhs {
							if lhs == sel {
								kind = "assignment"
								if len(a.Lhs) != 1 || len(a.Rhs) != 1 || a.Tok != token.ASSIGN {
									kind = "complex-assignment"
								}
							}
						}
					}
					if u, ok := parent.(*ast.UnaryExpr); ok && u.Op == token.AND {
						kind = "address"
					}
					sites = append(sites, Site{file, p.Fset.Position(n.Pos()).Line, sel.Sel.Name, fmt.Sprintf("%T", parent), kind})
					switch kind {
					case "read":
						add(sel.Sel.Pos(), sel.Sel.End(), names[sel.Sel.Name]+"()")
					case "assignment":
						a := parent.(*ast.AssignStmt)
						add(sel.Sel.Pos(), a.Rhs[0].Pos(), "Set"+sel.Sel.Name+"(")
						add(a.Rhs[0].End(), a.Rhs[0].End(), ")")
					case "address":
						u := parent.(*ast.UnaryExpr)
						add(u.OpPos, u.OpPos+1, "")
						add(sel.Sel.Pos(), sel.Sel.End(), sel.Sel.Name+"Slot()")
					default:
						panic("unsupported field use")
					}

				}
				if lit, ok := n.(*ast.CompositeLit); ok && isSymbol(p.TypesInfo.TypeOf(lit)) {
					for _, e := range lit.Elts {
						if kv, ok := e.(*ast.KeyValueExpr); ok {
							if key, ok := kv.Key.(*ast.Ident); ok && (key.Name == "Members" || key.Name == "Exports" || key.Name == "ExportSymbol") {
								sites = append(sites, Site{file, p.Fset.Position(kv.Pos()).Line, key.Name, "*ast.CompositeLit", "literal"})
							}
						}
					}
				}
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
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(struct {
		Sites        []Site
		Edits        []Edit
		SourceHashes map[string]string
	}{sites, edits, sourceHashes}); err != nil {
		panic(err)
	}
}
