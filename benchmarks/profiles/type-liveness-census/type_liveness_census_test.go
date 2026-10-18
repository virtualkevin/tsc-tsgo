package checker

import (
	"runtime"
	"testing"
)

func TestTypeLivenessDisabledAndConstruction(t *testing.T) {
	t.Setenv("TSC_GO_TYPE_LIVENESS_CENSUS", "")
	if newTypeLivenessCensus() != nil {
		t.Fatal("disabled observer")
	}
	c := &Checker{}
	if _, ok := c.TypeLivenessSnapshot(); ok {
		t.Fatal("disabled snapshot")
	}
	t.Setenv("TSC_GO_TYPE_LIVENESS_CENSUS", "unused.json")
	c.typeLivenessCensus = newTypeLivenessCensus()
	var keep []*Type
	for i := 0; i < 129; i++ {
		keep = append(keep, c.newIntrinsicType(TypeFlagsString, "x"))
	}
	r, ok := c.TypeLivenessSnapshot()
	if !ok || r.Created != 129 || r.SemanticTypeCount != 129 || r.Sampled != 3 || r.Eligible != 3 || r.Available != 3 || r.Cleared != 0 || r.IdentityMismatches != 0 {
		t.Fatalf("%+v", r)
	}
	if len(r.Kinds) != 1 || r.Kinds[0].CreationFlags != TypeFlagsString || r.Kinds[0].Sampled != 3 {
		t.Fatal(r.Kinds)
	}
	runtime.KeepAlive(keep)
}

func TestTypeLivenessBoundAndIdentity(t *testing.T) {
	c := &Checker{typeLivenessCensus: &typeLivenessCensus{}}
	value := &Type{id: 7, checker: c, flags: TypeFlagsNumber}
	count := typeLivenessStride*(typeLivenessLimit+2) + 1
	for i := uint64(0); i < count; i++ {
		c.typeLivenessCensus.observe(value)
	}
	r, _ := c.TypeLivenessSnapshot()
	if r.Created != count || r.Sampled != typeLivenessLimit || r.Overflow != 3 || r.Eligible != r.Sampled+r.Overflow || r.IdentityMismatches != 0 {
		t.Fatalf("%+v", r)
	}
	value.checker = &Checker{}
	r, _ = c.TypeLivenessSnapshot()
	if r.IdentityMismatches != r.Sampled {
		t.Fatal("owner mismatch not detected")
	}
	runtime.KeepAlive(value)
}

//go:noinline
func populateTypeLiveness(c *Checker) []*Type {
	var keep []*Type
	for i := 0; i < 4096; i++ {
		typ := c.newIntrinsicType(TypeFlagsString, "not-a-tiny-object")
		if i%128 == 0 {
			keep = append(keep, typ)
		}
	}
	return keep
}

func TestTypeLivenessDoesNotRetainUnreachableTypes(t *testing.T) {
	c := &Checker{typeLivenessCensus: &typeLivenessCensus{}}
	keep := populateTypeLiveness(c)
	for range 3 {
		runtime.GC()
	}
	r, _ := c.TypeLivenessSnapshot()
	if r.Sampled != 64 || r.Available < 32 || r.Cleared == 0 || r.Available+r.Cleared != 64 || r.IdentityMismatches != 0 {
		t.Fatalf("%+v", r)
	}
	// This checks observed reclamation on the pinned runtime, not a general weak
	// pointer guarantee that every unreachable value must eventually clear.
	for _, typ := range keep {
		if typ.checker != c || typ.id == 0 {
			t.Fatal("strongly held type lost")
		}
	}
	runtime.KeepAlive(keep)
	runtime.KeepAlive(c)
}
