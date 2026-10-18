package checker

// Classification reads existing discriminants only: no Map/Kind/query calls.
var windowTypeFamilyNames = [16]string{"parameter", "reference", "reverse-mapped", "object-instantiation", "other-object", "union", "intersection", "index", "indexed-access", "template", "string-mapping", "conditional", "substitution", "other", "reserved14", "reserved15"}
var windowMapperFamilyNames = [10]string{"nil", "simple", "array", "array-single", "deferred", "function", "merged", "composite", "inference", "other"}

type WindowFamilyCounts struct {
	Selected, FirstInWindow, RepeatedCompleted, NestedPending                                            uint64
	FinishedFirst, FinishedRepeated, EvictedBeforeFinish                                                 uint64
	SameResult, ChangedResult, SameStateAndResult                                                        uint64
	FirstDescendantInstantiations, RepeatedDescendantInstantiations, ZeroDescendantRepeats, CounterWraps uint64
}

func windowMapperFamily(m *TypeMapper) int {
	if m == nil {
		return 0
	}
	switch m.data.(type) {
	case *SimpleTypeMapper:
		return 1
	case *ArrayTypeMapper:
		return 2
	case *ArrayToSingleTypeMapper:
		return 3
	case *DeferredTypeMapper:
		return 4
	case *FunctionTypeMapper:
		return 5
	case *MergedTypeMapper:
		return 6
	case *CompositeTypeMapper:
		return 7
	case *InferenceTypeMapper:
		return 8
	default:
		return 9
	}
}
func windowTypeFamily(t *Type) int {
	f := t.flags
	switch {
	case f&TypeFlagsTypeParameter != 0:
		return 0
	case f&TypeFlagsObject != 0:
		o := t.objectFlags
		if o&(ObjectFlagsReference|ObjectFlagsAnonymous|ObjectFlagsMapped) != 0 {
			if o&ObjectFlagsReference != 0 && t.AsTypeReference().node == nil {
				return 1
			}
			if o&ObjectFlagsReverseMapped != 0 {
				return 2
			}
			return 3
		}
		return 4
	case f&TypeFlagsUnionOrIntersection != 0:
		if f&TypeFlagsUnion != 0 {
			return 5
		}
		return 6
	case f&TypeFlagsIndex != 0:
		return 7
	case f&TypeFlagsIndexedAccess != 0:
		return 8
	case f&TypeFlagsTemplateLiteral != 0:
		return 9
	case f&TypeFlagsStringMapping != 0:
		return 10
	case f&TypeFlagsConditional != 0:
		return 11
	case f&TypeFlagsSubstitution != 0:
		return 12
	default:
		return 13
	}
}
