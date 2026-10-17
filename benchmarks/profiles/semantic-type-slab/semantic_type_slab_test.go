package checker

import (
	"runtime"
	"testing"
	"weak"

	"github.com/microsoft/typescript-go/internal/ast"
)

func TestSemanticTypeSlabStableIdentityAndZeroState(t *testing.T) {
	c := &Checker{}
	objects := make([]*Type, 1025)
	references := make([]*Type, len(objects))
	for i := range objects {
		o := c.newObjectType(ObjectFlagsAnonymous, nil)
		r := c.newObjectType(ObjectFlagsReference, nil)
		if o.AsObjectType().properties != nil || r.AsTypeReference().target != nil {
			t.Fatal("new storage was not zeroed")
		}
		symbol := &ast.Symbol{Name: "retained"}
		o.AsObjectType().properties = []*ast.Symbol{symbol}
		r.AsTypeReference().target = o
		r.AsTypeReference().resolvedTypeArguments = []*Type{o}
		objects[i], references[i] = o, r
	}
	runtime.GC()
	other := &Checker{}
	for i, o := range objects {
		r := references[i]
		if o.id != TypeId(2*i+1) || r.id != TypeId(2*i+2) || o.checker != c || r.checker != c {
			t.Fatal("identity or ownership changed")
		}
		if o.AsObjectType().properties[0].Name != "retained" || r.AsTypeReference().target != o || r.AsTypeReference().resolvedTypeArguments[0] != o {
			t.Fatal("lost payload graph")
		}
		if o == other.newObjectType(ObjectFlagsAnonymous, nil) || r == other.newObjectType(ObjectFlagsReference, nil) {
			t.Fatal("storage shared across checkers")
		}
	}
	runtime.KeepAlive(objects)
	runtime.KeepAlive(references)
	runtime.KeepAlive(c)
	runtime.KeepAlive(other)
}

//go:noinline
func detachedSemanticTypeHeader() (Type, weak.Pointer[ObjectType], weak.Pointer[ast.Symbol]) {
	c := &Checker{}
	o := c.newObjectType(ObjectFlagsAnonymous, nil)
	symbol := &ast.Symbol{Name: "tail"}
	o.AsObjectType().properties = []*ast.Symbol{symbol}
	for range 100 {
		c.newObjectType(ObjectFlagsAnonymous, nil)
	}
	return *o, weak.Make(o.AsObjectType()), weak.Make(symbol)
}

func TestSemanticTypeSlabCopiedHeaderRetainsTail(t *testing.T) {
	copied, object, symbol := detachedSemanticTypeHeader()
	for range 3 {
		runtime.GC()
	}
	if object.Value() == nil || symbol.Value() == nil || copied.AsObjectType() != object.Value() || copied.AsObjectType().properties[0] != symbol.Value() {
		t.Fatal("copied header lost original allocation or tail")
	}
	runtime.KeepAlive(copied)
}

//go:noinline
func obsoleteSemanticSlabs() (*Checker, weak.Pointer[ObjectType], weak.Pointer[TypeReference]) {
	c := &Checker{}
	object := c.newObjectType(ObjectFlagsAnonymous, nil).AsObjectType()
	reference := c.newObjectType(ObjectFlagsReference, nil).AsTypeReference()
	a, b := weak.Make(object), weak.Make(reference)
	for range 96 {
		c.newObjectType(ObjectFlagsAnonymous, nil)
		c.newObjectType(ObjectFlagsReference, nil)
	}
	return c, a, b
}

func TestSemanticTypeSlabDoesNotRootObsoletePages(t *testing.T) {
	c, object, reference := obsoleteSemanticSlabs()
	for range 10 {
		runtime.GC()
		if object.Value() == nil && reference.Value() == nil {
			break
		}
	}
	if object.Value() != nil || reference.Value() != nil {
		t.Fatal("allocator retained obsolete pages without escaped objects")
	}
	runtime.KeepAlive(c)
}
