package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
)

// Diagnostic classification only: this does not change instantiation decisions.
// Categories are ordered exclusions followed by a syntactic candidate subset.
func primitivePropertyCategory(symbol *ast.Symbol) int {
	if symbol == nil || symbol.Flags&ast.SymbolFlagsProperty == 0 || symbol.Flags&^(ast.SymbolFlagsProperty|ast.SymbolFlagsOptional) != 0 {
		return 0
	}
	if symbol.CheckFlags != 0 {
		return 1
	}
	if len(symbol.Declarations) != 1 || symbol.ValueDeclaration == nil || symbol.Declarations[0] != symbol.ValueDeclaration {
		return 2
	}
	d := symbol.ValueDeclaration
	if d.Kind != ast.KindPropertySignature || d.Parent == nil || (d.Parent.Kind != ast.KindInterfaceDeclaration && d.Parent.Kind != ast.KindTypeLiteral) {
		return 3
	}
	if ast.IsInJSFile(d) {
		return 4
	}
	t := d.Type()
	if t == nil || d.Initializer() != nil {
		return 5
	}
	switch t.Kind {
	case ast.KindAnyKeyword, ast.KindUnknownKeyword, ast.KindStringKeyword, ast.KindNumberKeyword, ast.KindBigIntKeyword, ast.KindBooleanKeyword, ast.KindSymbolKeyword, ast.KindObjectKeyword, ast.KindVoidKeyword, ast.KindUndefinedKeyword, ast.KindNeverKeyword:
		return 7
	}
	return 6
}
func newPrimitivePropertyCensus() *[8]uint64 {
	if os.Getenv("TSC_GO_PRIMITIVE_PROPERTY_CENSUS") == "" {
		return nil
	}
	return new([8]uint64)
}

type PrimitivePropertySnapshot struct {
	CheckerID uint32
	Counts    [8]uint64
}

func (c *Checker) PrimitivePropertySnapshot() (PrimitivePropertySnapshot, bool) {
	if c.primitivePropertyCensus == nil {
		return PrimitivePropertySnapshot{}, false
	}
	return PrimitivePropertySnapshot{c.id, *c.primitivePropertyCensus}, true
}
func WritePrimitivePropertySnapshots(path string, owners []PrimitivePropertySnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Categories    [8]string
		Scope         string
		Owners        []PrimitivePropertySnapshot
	}{1, [8]string{"non-plain-property", "checker-metadata", "declaration-identity", "non-property-signature-or-parent", "javascript", "missing-annotation-or-initializer", "non-closed-keyword", "syntactic-candidate"}, "Ordered scalar classification at actual newInstantiatedSymbolWithLinks entries. Candidate subset is not a proven safe optimization or saved cost; frozen pending-member clone decisions may precede this entry.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
