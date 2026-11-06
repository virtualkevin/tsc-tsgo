package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"runtime"
	"testing"
)

func TestOptionalSymbolStorageCheckerClone(t *testing.T) {
	c := lazyPropertyTestChecker()
	c.mergedSymbols = make(map[*ast.Symbol]*ast.Symbol)
	original := c.newSymbol(ast.SymbolFlagsProperty, "source")
	member := c.newSymbol(ast.SymbolFlagsProperty, "member")
	export := c.newSymbol(ast.SymbolFlagsProperty, "export")
	original.Parent = member
	original.Members = ast.SymbolTable{"m": member}
	original.Exports = ast.SymbolTable{"e": export}
	original.ExportSymbol = export
	clone := c.cloneSymbol(original)
	if clone == original || clone.Parent != member || clone.Members["m"] != member || clone.Exports["e"] != export {
		t.Fatal("clone values/identity")
	}
	if clone.ExportSymbol != nil {
		t.Fatal("clone newly copied ExportSymbol")
	}
	delete(original.Members, "m")
	delete(clone.Exports, "e")
	if clone.Members["m"] != member || original.Exports["e"] != export {
		t.Fatal("clone maps share mutable backing")
	}
	old := clone.Members
	clone.Members = nil
	runtime.GC()
	if old["m"] != member {
		t.Fatal("old returned map lost")
	}
	empty := c.newSymbol(ast.SymbolFlagsProperty, "empty")
	empty.Exports = ast.SymbolTable{}
	copy := c.cloneSymbol(empty)
	if copy.Members != nil || copy.Exports == nil {
		t.Fatal("nil/empty map distinction lost")
	}
}
