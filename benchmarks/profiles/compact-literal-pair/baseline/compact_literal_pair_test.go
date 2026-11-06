package checker

import (
	"runtime"
	"testing"
	"unsafe"
)

func TestCompactLiteralPairStateAndCopies(t *testing.T) {
	c := lazyPropertyTestChecker()
	var zero LiteralType
	if zero.FreshType() != nil || zero.RegularType() != nil {
		t.Fatal("zero state")
	}
	r := c.newLiteralType(TypeFlagsStringLiteral, "value", nil)
	if r.AsLiteralType().RegularType() != r || r.AsLiteralType().FreshType() != nil {
		t.Fatal("regular initial state")
	}
	f := c.newLiteralType(TypeFlagsStringLiteral, "value", r)
	if f.AsLiteralType().RegularType() != r || f.AsLiteralType().FreshType() != nil {
		t.Fatal("fresh allocated state")
	}
	f.AsLiteralType().setFreshType(f)
	r.AsLiteralType().setFreshType(f)
	for _, original := range []*Type{r, f} {
		copy := *original.AsLiteralType()
		if copy.FreshType() != f || copy.RegularType() != r {
			t.Fatal("copied payload changed canonical identity")
		}
		header := *original
		if header.AsLiteralType().FreshType() != f || header.AsLiteralType().RegularType() != r {
			t.Fatal("copied header")
		}
	}
	if isFreshLiteralType(r) || !isFreshLiteralType(f) {
		t.Fatal("freshness")
	}
}

func TestCompactLiteralPairInterningAndGC(t *testing.T) {
	c := lazyPropertyTestChecker()
	start := c.TypeCount
	r := c.getStringLiteralType("unique literal fixture")
	f := c.getFreshTypeOfLiteralType(r)
	if c.TypeCount != start+2 {
		t.Fatal("allocation count")
	}
	for i := 0; i < 100; i++ {
		if c.getStringLiteralType("unique literal fixture") != r || c.getFreshTypeOfLiteralType(r) != f || c.getFreshTypeOfLiteralType(f) != f || c.getRegularTypeOfLiteralType(f) != r {
			t.Fatal("interning")
		}
	}
	if c.TypeCount != start+2 {
		t.Fatal("repeated allocation")
	}
	for i := 0; i < 3; i++ {
		runtime.GC()
	}
	if f.AsLiteralType().RegularType() != r || r.AsLiteralType().FreshType() != f {
		t.Fatal("lost partner")
	}
	runtime.KeepAlive(c)
}

func TestCompactLiteralPairLayout(t *testing.T) {
	if unsafe.Sizeof(Type{}) != 56 || unsafe.Sizeof(LiteralType{}) != 88 {
		t.Fatalf("unexpected sizes: %d %d", unsafe.Sizeof(Type{}), unsafe.Sizeof(LiteralType{}))
	}
	t.Logf("Type=%d LiteralType=%d", unsafe.Sizeof(Type{}), unsafe.Sizeof(LiteralType{}))
}
