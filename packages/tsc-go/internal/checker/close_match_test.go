package checker

import (
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
)

func TestWideUnionCloseMatchPrefilter(t *testing.T) {
	c := templateCacheTestChecker()
	left, right := &ast.Symbol{}, &ast.Symbol{}
	var forms []*Type
	for _, flags := range []TypeFlags{TypeFlagsObject, TypeFlagsString} {
		for _, symbol := range []*ast.Symbol{nil, left, right} {
			for _, aliasSymbol := range []*ast.Symbol{nil, left, right} {
				for _, args := range [][]*Type{nil, {c.stringType}} {
					forms = append(forms, &Type{flags: flags, symbol: symbol, alias: &TypeAlias{symbol: aliasSymbol, typeArguments: args}})
				}
			}
			forms = append(forms, &Type{flags: flags, symbol: symbol})
		}
	}
	for _, s := range forms {
		for _, target := range forms {
			if c.isTypeCloselyMatchedBy(s, target) && !mayHaveCloseMatch([]*Type{s}, []*Type{target}) {
				t.Fatal("prefilter excluded an object or alias match")
			}
		}
	}
	sources, targets := make([]*Type, 32), make([]*Type, 8)
	for i := range sources {
		sources[i] = &Type{flags: TypeFlagsObject, symbol: left}
	}
	for i := range targets {
		targets[i] = &Type{flags: TypeFlagsObject, symbol: right}
	}
	if mayHaveCloseMatch(sources, targets) {
		t.Fatal("disjoint symbol sets reported a possible match")
	}
	s, u := c.inferFromCloselyMatchingTypes(nil, sources, targets)
	if len(s) != len(sources) || len(u) != len(targets) || &s[0] != &sources[0] || &u[0] != &targets[0] {
		t.Fatal("disjoint pass changed its operands")
	}
}
