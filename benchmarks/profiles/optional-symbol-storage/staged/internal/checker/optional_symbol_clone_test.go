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
	original.SetMembers(ast.SymbolTable{"m": member})
	original.SetExports(ast.SymbolTable{"e": export})
	original.SetExportSymbol(export)
	clone := c.cloneSymbol(original)
	if clone == original || clone.Parent != member || clone.MembersTable()["m"] != member || clone.ExportsTable()["e"] != export {
		t.Fatal("clone values/identity")
	}
	if clone.ExportTarget() != nil {
		t.Fatal("clone newly copied ExportSymbol")
	}
	delete(original.MembersTable(), "m")
	delete(clone.ExportsTable(), "e")
	if clone.MembersTable()["m"] != member || original.ExportsTable()["e"] != export {
		t.Fatal("clone maps share mutable backing")
	}
	old := clone.MembersTable()
	clone.SetMembers(nil)
	runtime.GC()
	if old["m"] != member {
		t.Fatal("old returned map lost")
	}
	empty := c.newSymbol(ast.SymbolFlagsProperty, "empty")
	empty.SetExports(ast.SymbolTable{})
	copy := c.cloneSymbol(empty)
	if copy.MembersTable() != nil || copy.ExportsTable() == nil {
		t.Fatal("nil/empty map distinction lost")
	}
}
