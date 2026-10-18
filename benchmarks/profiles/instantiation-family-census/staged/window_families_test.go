package checker

import "testing"

func TestInstantiationWindowFamilyClassification(t *testing.T) {
	mappers := []TypeMapperData{&SimpleTypeMapper{}, &ArrayTypeMapper{}, &ArrayToSingleTypeMapper{}, &DeferredTypeMapper{}, &FunctionTypeMapper{}, &MergedTypeMapper{}, &CompositeTypeMapper{}, &InferenceTypeMapper{}, &TypeMapperBase{}}
	if windowMapperFamily(nil) != 0 {
		t.Fatal("nil mapper")
	}
	for i, m := range mappers {
		if got := windowMapperFamily(&TypeMapper{data: m}); got != i+1 {
			t.Fatalf("mapper %T: %d", m, got)
		}
	}
	flags := []TypeFlags{TypeFlagsTypeParameter, TypeFlagsObject, TypeFlagsUnion, TypeFlagsIntersection, TypeFlagsIndex, TypeFlagsIndexedAccess, TypeFlagsTemplateLiteral, TypeFlagsStringMapping, TypeFlagsConditional, TypeFlagsSubstitution, TypeFlagsString}
	want := []int{0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
	for i, f := range flags {
		if got := windowTypeFamily(&Type{flags: f}); got != want[i] {
			t.Fatalf("flags %d: %d", f, got)
		}
	}
	for _, o := range []ObjectFlags{ObjectFlagsAnonymous, ObjectFlagsMapped} {
		if windowTypeFamily(&Type{flags: TypeFlagsObject, objectFlags: o}) != 3 {
			t.Fatal("object instantiation")
		}
	}
	if windowTypeFamily(&Type{flags: TypeFlagsObject, objectFlags: ObjectFlagsMapped | ObjectFlagsReverseMapped}) != 2 {
		t.Fatal("reverse mapped")
	}
}
func TestInstantiationWindowFamilyRepeatAccounting(t *testing.T) {
	s := &instantiationWindow{slots: make([]windowEntry, 1)}
	c := &Checker{}
	input := &Type{id: 1, flags: TypeFlagsTypeParameter}
	m := newSimpleTypeMapper(input, input)
	a := s.begin(c, input, m, nil)
	s.finish(c, a, input)
	a = s.begin(c, input, m, nil)
	s.finish(c, a, input)
	a = s.begin(c, input, m, nil)
	c.TotalInstantiationCount += 2
	s.finish(c, a, &Type{id: 2})
	f := s.families[0][1]
	if f.Selected != 3 || f.FirstInWindow != 1 || f.RepeatedCompleted != 2 || f.FinishedRepeated != 2 || f.ZeroDescendantRepeats != 1 || f.RepeatedDescendantInstantiations != 2 || f.SameResult != 1 || f.ChangedResult != 1 || f.SameStateAndResult != 1 {
		t.Fatalf("%+v", f)
	}
	// Classification belongs to the request token even when later requests evict it.
	a = s.begin(c, input, m, nil)
	b := s.begin(c, &Type{id: 3, flags: TypeFlagsUnion}, m, nil)
	s.finish(c, b, input)
	s.finish(c, a, input)
	if s.families[0][1].EvictedBeforeFinish != 1 || s.families[5][1].FinishedFirst != 1 {
		t.Fatal("eviction attribution")
	}
}
