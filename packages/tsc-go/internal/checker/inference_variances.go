package checker

import "github.com/microsoft/typescript-go/internal/ast"

// Ports tsc-ts 6ca738bc3d40d99615eb6427f4bf43c95c512614.
func (c *Checker) someTypeCouldHoldInference(targets []*Type) bool {
	for _, t := range targets {
		if c.couldHoldInference(t, 0) {
			return true
		}
	}
	return false
}

// Refine two conservative couldContainTypeVariables answers: resolved deferred
// references without aliases contain inference targets only in their arguments;
// top-level class static sides contain none outside generic signatures, which
// inference erases. Never resolve arguments just to answer this question.
func (c *Checker) couldHoldInference(t *Type, depth int) bool {
	if !c.couldContainTypeVariables(t) {
		return false
	}
	if t.alias != nil || depth == 4 {
		return true
	}
	if t.objectFlags&ObjectFlagsReference != 0 {
		resolved := t.AsTypeReference().resolvedTypeArguments
		if resolved == nil {
			return true
		}
		for _, argument := range resolved {
			if c.couldHoldInference(argument, depth+1) {
				return true
			}
		}
		return false
	}
	return !isTopLevelClassStaticSide(t)
}

func isTopLevelClassStaticSide(t *Type) bool {
	symbol := t.symbol
	if t.objectFlags&ObjectFlagsAnonymous == 0 || symbol == nil || symbol.Flags&ast.SymbolFlagsClass == 0 ||
		symbol.Flags&(ast.SymbolFlagsFunction|ast.SymbolFlagsMethod|ast.SymbolFlagsTypeLiteral|ast.SymbolFlagsObjectLiteral) != 0 || len(symbol.Declarations) == 0 {
		return false
	}
	for _, declaration := range symbol.Declarations {
		switch declaration.Kind {
		case ast.KindClassDeclaration, ast.KindInterfaceDeclaration, ast.KindModuleDeclaration:
		default:
			return false
		}
		for parent := declaration.Parent; parent == nil || parent.Kind != ast.KindSourceFile; parent = parent.Parent {
			if parent == nil || parent.Kind != ast.KindModuleBlock && parent.Kind != ast.KindModuleDeclaration {
				return false
			}
		}
	}
	return true
}
