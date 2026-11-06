package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"runtime"
	"testing"
	"unsafe"
)

func TestInstantiatedSymbolCoallocationIdentity(t *testing.T) {
	c := lazyPropertyTestChecker()
	original := c.newSymbol(ast.SymbolFlagsProperty, "item")
	original.CheckFlags = ast.CheckFlagsReadonly | ast.CheckFlagsOptionalParameter
	parameter := c.newTypeParameter(nil)
	literal := c.newLiteralType(TypeFlagsStringLiteral, "value", nil)
	c.valueSymbolLinks.Get(original).resolvedType = parameter
	mapper := newSimpleTypeMapper(parameter, literal)
	count := c.SymbolCount
	first := c.newInstantiatedSymbol(original, mapper)
	links := c.valueSymbolLinks.Get(first)
	for range 2048 {
		c.newInstantiatedSymbol(original, mapper)
	}
	runtime.GC()
	if c.SymbolCount != count+2049 || c.getTypeOfSymbol(first) != literal || links.target != original || links.mapper != mapper {
		t.Fatal("constructor state or resolved identity changed")
	}
	if first.CheckFlags != ast.CheckFlagsInstantiated|original.CheckFlags {
		t.Fatal("flags changed")
	}
	second := c.newInstantiatedSymbol(first, mapper)
	if second == first || c.valueSymbolLinks.Get(second) == links || c.valueSymbolLinks.Get(second).target != original {
		t.Fatal("nested instantiation identity changed")
	}
	replacement := c.valueSymbolLinks.New(first)
	if replacement == links || links.resolvedType != literal || links.target != original {
		t.Fatal("replacement invalidated old record")
	}
	runtime.GC()
	if first.Name != "item" || links.resolvedType != literal {
		t.Fatal("published members lost")
	}
	t.Logf("layout symbol=%d links=%d record=%d", unsafe.Sizeof(ast.Symbol{}), unsafe.Sizeof(ValueSymbolLinks{}), unsafe.Sizeof(instantiatedSymbolRecord{}))
	runtime.KeepAlive(c)
}
