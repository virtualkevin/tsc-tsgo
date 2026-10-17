package checker

import (
	"runtime"
	"testing"
	"weak"

	"github.com/microsoft/typescript-go/internal/ast"
)

type nodeLinksProbe struct {
	node      weak.Pointer[ast.Node]
	symbol    weak.Pointer[SymbolNodeLinks]
	signature weak.Pointer[SignatureLinks]
	typ       weak.Pointer[TypeNodeLinks]
}

//go:noinline
func populateNodeLinks(c *Checker, count int) []nodeLinksProbe {
	factory := ast.NewNodeFactory(ast.NodeFactoryHooks{})
	probes := make([]nodeLinksProbe, count)
	for i := range probes {
		node := factory.NewIdentifier("same-text")
		symbol := c.symbolNodeLinks.Get(node)
		signature := c.signatureLinks.Get(node)
		typ := c.typeNodeLinks.Get(node)
		symbol.resolvedSymbol = &ast.Symbol{Name: "retained"}
		signature.resolvedSignature = &Signature{}
		signature.effectsSignature = &Signature{}
		signature.decoratorSignature = &Signature{}
		typ.resolvedType = &Type{flags: TypeFlagsString}
		typ.outerTypeParameters = []*Type{{flags: TypeFlagsNumber}}
		probes[i] = nodeLinksProbe{weak.Make(node), weak.Make(symbol), weak.Make(signature), weak.Make(typ)}
	}
	return probes
}

func TestNodeLinksRetainGraphsAcrossGrowthAndGC(t *testing.T) {
	c := &Checker{}
	probes := populateNodeLinks(c, 4096)
	for range 3 {
		runtime.GC()
	}
	other := &Checker{}
	for i, probe := range probes {
		node, symbol, signature, typ := probe.node.Value(), probe.symbol.Value(), probe.signature.Value(), probe.typ.Value()
		if node == nil || symbol == nil || signature == nil || typ == nil {
			t.Fatalf("lost key or links at %d", i)
		}
		if node.Text() != "same-text" || c.symbolNodeLinks.Get(node) != symbol || c.signatureLinks.Get(node) != signature || c.typeNodeLinks.Get(node) != typ {
			t.Fatal("key or stable slot identity changed")
		}
		if symbol.resolvedSymbol == nil || symbol.resolvedSymbol.Name != "retained" || signature.resolvedSignature == nil || signature.effectsSignature == nil || signature.decoratorSignature == nil || typ.resolvedType.flags != TypeFlagsString || len(typ.outerTypeParameters) != 1 || typ.outerTypeParameters[0].flags != TypeFlagsNumber {
			t.Fatal("lost links payload graph")
		}
		if other.symbolNodeLinks.Get(node) == symbol || other.signatureLinks.Get(node) == signature || other.typeNodeLinks.Get(node) == typ {
			t.Fatal("checker ownership crossed")
		}
	}
	runtime.KeepAlive(c)
	runtime.KeepAlive(other)
}
