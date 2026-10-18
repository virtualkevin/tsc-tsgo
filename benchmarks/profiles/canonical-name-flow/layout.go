package main

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"runtime"
	"sync/atomic"
	"unique"
	"unsafe"
)

type symbolWithNameHandle struct {
	Flags            ast.SymbolFlags
	CheckFlags       ast.CheckFlags
	Name             unique.Handle[string]
	Declarations     []*ast.Node
	ValueDeclaration *ast.Node
	Members          map[unique.Handle[string]]*ast.Symbol
	Exports          map[unique.Handle[string]]*ast.Symbol
	id               atomic.Uint64
	Parent           *ast.Symbol
	ExportSymbol     *ast.Symbol
}
type identifierWithNameHandle struct {
	ast.PrimaryExpressionBase
	ast.FlowNodeBase
	Text unique.Handle[string]
}

func main() {
	out := struct {
		GoVersion, Arch, Scope string
		Sizes                  map[string]uintptr
	}{runtime.Version(), runtime.GOARCH, "Layout-only mirror, not a compiler candidate or actual map-group/allocation/RSS measurement. Canonical objects, cloned string bytes, trie nodes, weak-pointer cleanup and conversion costs are excluded.", map[string]uintptr{
		"string": unsafe.Sizeof(string("")), "handle": unsafe.Sizeof(unique.Handle[string]{}),
		"currentSymbol": unsafe.Sizeof(ast.Symbol{}), "proposedSymbolMirror": unsafe.Sizeof(symbolWithNameHandle{}),
		"currentIdentifier": unsafe.Sizeof(ast.Identifier{}), "proposedIdentifierMirror": unsafe.Sizeof(identifierWithNameHandle{}),
		"stringSymbolEntryMirror": unsafe.Sizeof(struct {
			Key   string
			Value *ast.Symbol
		}{}), "handleSymbolEntryMirror": unsafe.Sizeof(struct {
			Key   unique.Handle[string]
			Value *ast.Symbol
		}{}),
	}}
	e := json.NewEncoder(os.Stdout)
	e.SetIndent("", "  ")
	if err := e.Encode(out); err != nil {
		panic(err)
	}
}
