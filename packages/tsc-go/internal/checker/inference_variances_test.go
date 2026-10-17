package checker

import (
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
)

func TestInferenceVariancesConcreteReferencesSkipMeasurement(t *testing.T) {
	c := &Checker{}
	c.couldContainTypeVariables = c.couldContainTypeVariablesWorker
	parameter := c.newTypeParameter(nil)
	generic := c.newObjectType(ObjectFlagsInterface|ObjectFlagsReference, &ast.Symbol{Name: "Generic", Flags: ast.SymbolFlagsInterface})
	generic.AsInterfaceType().allTypeParameters = []*Type{parameter}
	reference := c.newObjectType(ObjectFlagsReference, generic.symbol)
	reference.AsTypeReference().target = generic
	reference.AsTypeReference().resolvedTypeArguments = []*Type{c.newIntrinsicType(TypeFlagsString, "string")}
	n := &InferenceState{}
	c.inferFromReferenceTypeArguments(n, reference, reference)
	if c.varianceLinks.Has(generic.symbol) {
		t.Fatal("concrete reference inference measured generic variances")
	}
	if n.depth != 0 || len(n.inferences) != 0 {
		t.Fatal("concrete reference inference changed inference state")
	}
}

func TestInferenceVariancesDeferredArgumentsStayConservative(t *testing.T) {
	c := &Checker{}
	c.couldContainTypeVariables = c.couldContainTypeVariablesWorker
	concrete := c.newIntrinsicType(TypeFlagsString, "string")
	parameter := c.newTypeParameter(nil)
	reference := func(arguments []*Type) *Type {
		result := c.newObjectType(ObjectFlagsReference, nil)
		result.AsTypeReference().node = &ast.Node{Kind: ast.KindTypeReference}
		result.AsTypeReference().resolvedTypeArguments = arguments
		return result
	}
	resolved := reference([]*Type{concrete})
	if !c.couldContainTypeVariables(resolved) || c.couldHoldInference(resolved, 0) {
		t.Fatal("resolved concrete deferred reference should refine the conservative answer")
	}
	unresolved := reference(nil)
	if !c.couldHoldInference(unresolved, 0) || unresolved.AsTypeReference().resolvedTypeArguments != nil {
		t.Fatal("unresolved reference must remain conservative without resolving arguments")
	}
	if !c.couldHoldInference(reference([]*Type{parameter}), 0) {
		t.Fatal("generic argument lost its inference")
	}
	aliased := reference([]*Type{concrete})
	aliased.alias = &TypeAlias{symbol: &ast.Symbol{}, typeArguments: []*Type{concrete}}
	if !c.couldHoldInference(aliased, 0) {
		t.Fatal("alias must retain its conservative inference behavior")
	}
	deep := concrete
	for range 4 {
		deep = reference([]*Type{deep})
	}
	if c.couldHoldInference(deep, 0) {
		t.Fatal("concrete primitive at depth four should still reject inference")
	}
	deep = reference([]*Type{deep})
	if !c.couldHoldInference(deep, 0) {
		t.Fatal("structured types at depth four must retain conservative behavior")
	}
	cycle := reference([]*Type{concrete})
	cycle.AsTypeReference().resolvedTypeArguments[0] = cycle
	if !c.couldHoldInference(cycle, 0) {
		t.Fatal("recursive references must terminate conservatively")
	}
}

func TestInferenceVariancesClassStaticSideGuards(t *testing.T) {
	c := &Checker{}
	c.couldContainTypeVariables = c.couldContainTypeVariablesWorker
	file := &ast.Node{Kind: ast.KindSourceFile}
	module := &ast.Node{Kind: ast.KindModuleDeclaration, Parent: file}
	block := &ast.Node{Kind: ast.KindModuleBlock, Parent: module}
	local := &ast.Node{Kind: ast.KindFunctionDeclaration, Parent: file}
	for _, test := range []struct {
		name         string
		flags        ast.SymbolFlags
		declarations []*ast.Node
		want         bool
	}{
		{"file class", ast.SymbolFlagsClass, []*ast.Node{{Kind: ast.KindClassDeclaration, Parent: file}}, false},
		{"namespace class", ast.SymbolFlagsClass, []*ast.Node{{Kind: ast.KindClassDeclaration, Parent: block}}, false},
		{"merged interface", ast.SymbolFlagsClass, []*ast.Node{{Kind: ast.KindClassDeclaration, Parent: file}, {Kind: ast.KindInterfaceDeclaration, Parent: file}}, false},
		{"merged namespace", ast.SymbolFlagsClass, []*ast.Node{{Kind: ast.KindClassDeclaration, Parent: file}, module}, false},
		{"local class", ast.SymbolFlagsClass, []*ast.Node{{Kind: ast.KindClassDeclaration, Parent: local}}, true},
		{"class expression", ast.SymbolFlagsClass, []*ast.Node{{Kind: ast.KindClassExpression, Parent: file}}, true},
		{"mixed function", ast.SymbolFlagsClass | ast.SymbolFlagsFunction, []*ast.Node{{Kind: ast.KindClassDeclaration, Parent: file}}, true},
		{"mixed declaration", ast.SymbolFlagsClass, []*ast.Node{{Kind: ast.KindClassDeclaration, Parent: file}, {Kind: ast.KindFunctionDeclaration, Parent: file}}, true},
	} {
		t.Run(test.name, func(t *testing.T) {
			typ := c.newObjectType(ObjectFlagsAnonymous, &ast.Symbol{Flags: test.flags, Declarations: test.declarations})
			if got := c.couldHoldInference(typ, 0); got != test.want {
				t.Fatalf("could hold inference = %v, want %v", got, test.want)
			}
		})
	}
}
