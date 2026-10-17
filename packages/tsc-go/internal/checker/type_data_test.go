package checker

import (
	"reflect"
	"runtime"
	"testing"
	"unsafe"

	"github.com/microsoft/typescript-go/internal/ast"
)

type retainedTypeHeader struct {
	flags       TypeFlags
	objectFlags ObjectFlags
	id          TypeId
	symbol      *ast.Symbol
	alias       *TypeAlias
	checker     *Checker
	data        TypeData
}

func TestTypeDataHeaderLayout(t *testing.T) {
	oldSize, newSize := unsafe.Sizeof(retainedTypeHeader{}), unsafe.Sizeof(Type{})
	t.Logf("Type header: interface=%d bytes, pointer/tag=%d bytes", oldSize, newSize)
	if unsafe.Sizeof(uintptr(0)) == 8 && (oldSize != 56 || newSize != 48 || unsafe.Offsetof(Type{}.dataKind) != 12) {
		t.Fatalf("unexpected 64-bit layout: old=%d new=%d kind offset=%d", oldSize, newSize, unsafe.Offsetof(Type{}.dataKind))
	}
	if newSize > oldSize {
		t.Fatalf("header grew: %d > %d", newSize, oldSize)
	}
}

func mustTypeDataPanic(t *testing.T, call func()) {
	t.Helper()
	defer func() {
		if recover() == nil {
			t.Error("invalid conversion did not panic")
		}
	}()
	call()
}

func TestTypeDataAccessorContracts(t *testing.T) {
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

func TestTypeDataRetainsConcreteTailAcrossGC(t *testing.T) {
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
	if unsafe.Pointer(restored) != copied.data {
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

// Dynamic shape construction is test-only; production constructors never dispatch
// through TypeData or a concrete type switch.
func newTestTypeData(c *Checker, flags TypeFlags, objectFlags ObjectFlags, data TypeData) *Type {
	switch d := data.(type) {
	case *TypeBase:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataTypeBase)
	case *IntrinsicType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataIntrinsicType)
	case *LiteralType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataLiteralType)
	case *UniqueESSymbolType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataUniqueESSymbolType)
	case *ConstrainedType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataConstrainedType)
	case *StructuredType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataStructuredType)
	case *ObjectType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataObjectType)
	case *TypeReference:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataTypeReference)
	case *InterfaceType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataInterfaceType)
	case *TupleType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataTupleType)
	case *InstantiationExpressionType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataInstantiationExpressionType)
	case *MappedType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataMappedType)
	case *ReverseMappedType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataReverseMappedType)
	case *EvolvingArrayType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataEvolvingArrayType)
	case *UnionOrIntersectionType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataUnionOrIntersectionType)
	case *UnionType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataUnionType)
	case *IntersectionType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataIntersectionType)
	case *TypeParameter:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataTypeParameter)
	case *IndexType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataIndexType)
	case *IndexedAccessType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataIndexedAccessType)
	case *TemplateLiteralType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataTemplateLiteralType)
	case *StringMappingType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataStringMappingType)
	case *SubstitutionType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataSubstitutionType)
	case *ConditionalType:
		return c.newType(flags, objectFlags, unsafe.Pointer(d), typeDataConditionalType)
	default:
		panic("unsupported test TypeData")
	}
}

func TestTypeDataProductionConstructors(t *testing.T) {
	checker := &Checker{}
	primitive := checker.newIntrinsicType(TypeFlagsString, "constructor-input")
	cases := []struct {
		name     string
		makeType func() *Type
		kind     typeDataKind
		flags    TypeFlags
	}{
		{"intrinsic", func() *Type { return checker.newIntrinsicType(TypeFlagsString, "value") }, typeDataIntrinsicType, TypeFlagsString},
		{"literal", func() *Type { return checker.newLiteralType(TypeFlagsStringLiteral, "value", nil) }, typeDataLiteralType, TypeFlagsStringLiteral},
		{"uniqueSymbol", func() *Type { return checker.newUniqueESSymbolType(nil, "value") }, typeDataUniqueESSymbolType, TypeFlagsUniqueESSymbol},
		{"parameter", func() *Type { return checker.newTypeParameter(nil) }, typeDataTypeParameter, TypeFlagsTypeParameter},
		{"union", func() *Type { return checker.newUnionType(ObjectFlagsNone, []*Type{primitive}) }, typeDataUnionType, TypeFlagsUnion},
		{"intersection", func() *Type { return checker.newIntersectionType(ObjectFlagsNone, []*Type{primitive}) }, typeDataIntersectionType, TypeFlagsIntersection},
		{"indexedAccess", func() *Type { return checker.newIndexedAccessType(primitive, primitive, AccessFlagsNone) }, typeDataIndexedAccessType, TypeFlagsIndexedAccess},
		{"index", func() *Type { return checker.newIndexType(primitive, IndexFlagsNone) }, typeDataIndexType, TypeFlagsIndex},
		{"template", func() *Type { return checker.newTemplateLiteralType([]string{"", ""}, []*Type{primitive}) }, typeDataTemplateLiteralType, TypeFlagsTemplateLiteral},
		{"mapping", func() *Type { return checker.newStringMappingType(nil, primitive) }, typeDataStringMappingType, TypeFlagsStringMapping},
		{"conditional", func() *Type {
			return checker.newConditionalType(&ConditionalRoot{checkType: primitive, extendsType: primitive}, nil, nil)
		}, typeDataConditionalType, TypeFlagsConditional},
		{"substitution", func() *Type { return checker.newSubstitutionType(primitive, primitive) }, typeDataSubstitutionType, TypeFlagsSubstitution},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			before := checker.TypeCount
			typ := tc.makeType()
			if typ.dataKind != tc.kind || typ.flags != tc.flags || typ.id != TypeId(before+1) || checker.TypeCount != before+1 || typ.checker != checker || typ.data != unsafe.Pointer(typ) {
				t.Fatalf("incorrect allocation initialization: kind=%d flags=%d id=%d", typ.dataKind, typ.flags, typ.id)
			}
		})
	}
	objects := []struct {
		flags ObjectFlags
		kind  typeDataKind
	}{
		{ObjectFlagsInterface, typeDataInterfaceType},
		{ObjectFlagsClass, typeDataInterfaceType},
		{ObjectFlagsTuple, typeDataTupleType},
		{ObjectFlagsReference, typeDataTypeReference},
		{ObjectFlagsMapped, typeDataMappedType},
		{ObjectFlagsReverseMapped, typeDataReverseMappedType},
		{ObjectFlagsEvolvingArray, typeDataEvolvingArrayType},
		{ObjectFlagsInstantiationExpressionType, typeDataInstantiationExpressionType},
		{ObjectFlagsAnonymous, typeDataObjectType},
	}
	for _, tc := range objects {
		symbol := &ast.Symbol{}
		typ := checker.newObjectType(tc.flags, symbol)
		if typ.dataKind != tc.kind || typ.symbol != symbol || typ.AsObjectType() == nil || typ.data != unsafe.Pointer(typ) {
			t.Fatalf("incorrect object allocation for flags=%d: kind=%d", tc.flags, typ.dataKind)
		}
		// Cloned/instantiated object flags cannot change the allocation kind.
		typ.objectFlags = ObjectFlagsMapped | ObjectFlagsReference
		if typ.dataKind != tc.kind {
			t.Fatal("semantic flags changed allocation kind")
		}
	}
}
