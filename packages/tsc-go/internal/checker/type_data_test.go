package checker

import (
	"reflect"
	"runtime"
	"testing"
)

func mustTypeDataPanic(t *testing.T, call func()) {
	t.Helper()
	defer func() {
		if recover() == nil {
			t.Error("invalid conversion did not panic")
		}
	}()
	call()
}

func TestTypeAccessorContracts(t *testing.T) {
	allocations := []TypeData{
		&TypeBase{},
		&IntrinsicType{},
		&LiteralType{},
		&UniqueESSymbolType{},
		&ConstrainedType{},
		&StructuredType{},
		&ObjectType{},
		&TypeReference{},
		&InterfaceType{},
		&TupleType{},
		&InstantiationExpressionType{},
		&MappedType{},
		&ReverseMappedType{},
		&EvolvingArrayType{},
		&UnionOrIntersectionType{},
		&UnionType{},
		&IntersectionType{},
		&TypeParameter{},
		&IndexType{},
		&IndexedAccessType{},
		&TemplateLiteralType{},
		&StringMappingType{},
		&SubstitutionType{},
		&ConditionalType{},
	}
	concrete := []string{"AsIntrinsicType", "AsLiteralType", "AsUniqueESSymbolType", "AsTupleType", "AsInstantiationExpressionType", "AsMappedType", "AsReverseMappedType", "AsEvolvingArrayType", "AsTypeParameter", "AsUnionType", "AsIntersectionType", "AsIndexType", "AsIndexedAccessType", "AsTemplateLiteralType", "AsStringMappingType", "AsSubstitutionType", "AsConditionalType"}
	embedded := []string{"AsConstrainedType", "AsStructuredType", "AsObjectType", "AsTypeReference", "AsInterfaceType", "AsUnionOrIntersectionType"}
	for _, allocation := range allocations {
		name := reflect.TypeOf(allocation).Elem().Name()
		t.Run(name, func(t *testing.T) {
			checker := &Checker{}
			typ := newTestTypeData(checker, TypeFlagsNone, ObjectFlagsNone, allocation)
			if typ != allocation.AsType() {
				t.Fatal("constructor changed Type identity")
			}
			// Semantic flags mutate independently of concrete allocation identity.
			typ.flags = TypeFlagsUnion | TypeFlagsObject
			typ.objectFlags = ObjectFlagsReference | ObjectFlagsMapped
			for _, method := range embedded {
				got := reflect.ValueOf(typ).MethodByName(method).Call(nil)[0].Interface()
				want := reflect.ValueOf(allocation).MethodByName(method).Call(nil)[0].Interface()
				if !reflect.DeepEqual(got, want) {
					t.Errorf("%s: got %v, want %v", method, got, want)
				}
				// Pointer identity is required too, including embedded prefixes.
				if reflect.ValueOf(got).Pointer() != reflect.ValueOf(want).Pointer() {
					t.Errorf("%s: pointer identity changed", method)
				}
			}
			for _, method := range concrete {
				call := func() { reflect.ValueOf(typ).MethodByName(method).Call(nil) }
				if method == "As"+name {
					got := reflect.ValueOf(typ).MethodByName(method).Call(nil)[0].Pointer()
					if got != reflect.ValueOf(allocation).Pointer() {
						t.Errorf("%s: allocation identity changed", method)
					}
				} else {
					mustTypeDataPanic(t, call)
				}
			}
		})
	}
	for _, typ := range []*Type{nil, {}} {
		for _, method := range append(concrete, embedded...) {
			mustTypeDataPanic(t, func() { reflect.ValueOf(typ).MethodByName(method).Call(nil) })
		}
	}
}

func TestTypeRetainsConcreteTailAcrossGC(t *testing.T) {
	// Keep only the embedded Type reachable; no concrete or tail local survives.
	makeType := func() *Type {
		checker := &Checker{}
		data := &ConditionalType{}
		data.root = &ConditionalRoot{checkType: checker.newIntrinsicType(TypeFlagsString, "kept-alive")}
		return newTestTypeData(checker, TypeFlagsConditional, ObjectFlagsNone, data)
	}
	typ := makeType()
	for range 3 {
		runtime.GC()
	}
	if got := typ.AsConditionalType().root.checkType.AsIntrinsicType().IntrinsicName(); got != "kept-alive" {
		t.Fatalf("lost tail: %q", got)
	}
	runtime.KeepAlive(typ)
}

func TestCopiedTypeHeaderRetainsOriginalAllocation(t *testing.T) {
	// The detached header must keep the original allocation alive through data.
	// Do not retain the concrete pointer or its embedded Type elsewhere.
	makeCopy := func() Type {
		checker := &Checker{}
		data := &ConditionalType{}
		data.root = &ConditionalRoot{checkType: checker.newIntrinsicType(TypeFlagsString, "copied-header-tail")}
		return *newTestTypeData(checker, TypeFlagsConditional, ObjectFlagsNone, data)
	}
	copied := makeCopy()
	for range 3 {
		runtime.GC()
	}
	restored := copied.AsConditionalType()
	if restored.AsType() == &copied {
		t.Fatal("copied header was mistaken for the original concrete allocation")
	}
	if restored != copied.data.(*ConditionalType) {
		t.Fatal("accessor did not restore the retained original allocation pointer")
	}
	if restored.AsType().data != copied.data || restored.AsType().id != copied.id {
		t.Fatal("copied header lost the original allocation identity")
	}
	if got := restored.root.checkType.AsIntrinsicType().IntrinsicName(); got != "copied-header-tail" {
		t.Fatalf("lost original concrete tail: %q", got)
	}
	runtime.KeepAlive(copied)
}

// Keep the representation-independent contract tests reusable across experiments.
func newTestTypeData(c *Checker, flags TypeFlags, objectFlags ObjectFlags, data TypeData) *Type {
	return c.newType(flags, objectFlags, data)
}
