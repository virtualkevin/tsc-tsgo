package checker

// typeDataKind is immutable allocation identity, independent of semantic flags.
// Depth-first ordering makes each embedded-base family a contiguous range.
// Zero denotes an uninitialized Type. New kinds must preserve this hierarchy;
// the accessor matrix and compile-time layout assertions guard those assumptions.
type typeDataKind uint8

const (
	typeDataUninitialized typeDataKind = iota
	typeDataTypeBase
	typeDataIntrinsicType
	typeDataLiteralType
	typeDataUniqueESSymbolType
	typeDataConstrainedType
	typeDataStructuredType
	typeDataObjectType
	typeDataTypeReference
	typeDataInterfaceType
	typeDataTupleType
	typeDataInstantiationExpressionType
	typeDataMappedType
	typeDataReverseMappedType
	typeDataEvolvingArrayType
	typeDataUnionOrIntersectionType
	typeDataUnionType
	typeDataIntersectionType
	typeDataTypeParameter
	typeDataIndexType
	typeDataIndexedAccessType
	typeDataTemplateLiteralType
	typeDataStringMappingType
	typeDataSubstitutionType
	typeDataConditionalType
)

func (t *Type) requireTypeDataKind(kind typeDataKind) {
	if t.dataKind != kind {
		panic("invalid concrete Type conversion")
	}
}

// Exact accessors restore only the original allocation type.
func (t *Type) AsIntrinsicType() *IntrinsicType {
	t.requireTypeDataKind(typeDataIntrinsicType)
	return (*IntrinsicType)(t.data)
}
func (t *Type) AsLiteralType() *LiteralType {
	t.requireTypeDataKind(typeDataLiteralType)
	return (*LiteralType)(t.data)
}
func (t *Type) AsUniqueESSymbolType() *UniqueESSymbolType {
	t.requireTypeDataKind(typeDataUniqueESSymbolType)
	return (*UniqueESSymbolType)(t.data)
}
func (t *Type) AsTupleType() *TupleType {
	t.requireTypeDataKind(typeDataTupleType)
	return (*TupleType)(t.data)
}
func (t *Type) AsInstantiationExpressionType() *InstantiationExpressionType {
	t.requireTypeDataKind(typeDataInstantiationExpressionType)
	return (*InstantiationExpressionType)(t.data)
}
func (t *Type) AsMappedType() *MappedType {
	t.requireTypeDataKind(typeDataMappedType)
	return (*MappedType)(t.data)
}
func (t *Type) AsReverseMappedType() *ReverseMappedType {
	t.requireTypeDataKind(typeDataReverseMappedType)
	return (*ReverseMappedType)(t.data)
}
func (t *Type) AsEvolvingArrayType() *EvolvingArrayType {
	t.requireTypeDataKind(typeDataEvolvingArrayType)
	return (*EvolvingArrayType)(t.data)
}
func (t *Type) AsTypeParameter() *TypeParameter {
	t.requireTypeDataKind(typeDataTypeParameter)
	return (*TypeParameter)(t.data)
}
func (t *Type) AsUnionType() *UnionType {
	t.requireTypeDataKind(typeDataUnionType)
	return (*UnionType)(t.data)
}
func (t *Type) AsIntersectionType() *IntersectionType {
	t.requireTypeDataKind(typeDataIntersectionType)
	return (*IntersectionType)(t.data)
}
func (t *Type) AsIndexType() *IndexType {
	t.requireTypeDataKind(typeDataIndexType)
	return (*IndexType)(t.data)
}
func (t *Type) AsIndexedAccessType() *IndexedAccessType {
	t.requireTypeDataKind(typeDataIndexedAccessType)
	return (*IndexedAccessType)(t.data)
}
func (t *Type) AsTemplateLiteralType() *TemplateLiteralType {
	t.requireTypeDataKind(typeDataTemplateLiteralType)
	return (*TemplateLiteralType)(t.data)
}
func (t *Type) AsStringMappingType() *StringMappingType {
	t.requireTypeDataKind(typeDataStringMappingType)
	return (*StringMappingType)(t.data)
}
func (t *Type) AsSubstitutionType() *SubstitutionType {
	t.requireTypeDataKind(typeDataSubstitutionType)
	return (*SubstitutionType)(t.data)
}
func (t *Type) AsConditionalType() *ConditionalType {
	t.requireTypeDataKind(typeDataConditionalType)
	return (*ConditionalType)(t.data)
}

// Embedded accessors narrow the original allocation pointer to a zero-offset
// base prefix that is no larger and has exactly the same prefix layout. These
// never convert an embedded *Type pointer into a larger enclosing allocation.
func (t *Type) AsConstrainedType() *ConstrainedType {
	kind := t.dataKind
	if kind == typeDataUninitialized {
		panic("uninitialized Type conversion")
	}
	if kind-typeDataConstrainedType <= typeDataConditionalType-typeDataConstrainedType {
		return (*ConstrainedType)(t.data)
	}
	return nil
}
func (t *Type) AsStructuredType() *StructuredType {
	kind := t.dataKind
	if kind == typeDataUninitialized {
		panic("uninitialized Type conversion")
	}
	if kind-typeDataStructuredType <= typeDataIntersectionType-typeDataStructuredType {
		return (*StructuredType)(t.data)
	}
	return nil
}
func (t *Type) AsObjectType() *ObjectType {
	kind := t.dataKind
	if kind == typeDataUninitialized {
		panic("uninitialized Type conversion")
	}
	if kind-typeDataObjectType <= typeDataEvolvingArrayType-typeDataObjectType {
		return (*ObjectType)(t.data)
	}
	return nil
}
func (t *Type) AsTypeReference() *TypeReference {
	kind := t.dataKind
	if kind == typeDataUninitialized {
		panic("uninitialized Type conversion")
	}
	if kind-typeDataTypeReference <= typeDataTupleType-typeDataTypeReference {
		return (*TypeReference)(t.data)
	}
	return nil
}
func (t *Type) AsInterfaceType() *InterfaceType {
	kind := t.dataKind
	if kind == typeDataUninitialized {
		panic("uninitialized Type conversion")
	}
	if kind-typeDataInterfaceType <= typeDataTupleType-typeDataInterfaceType {
		return (*InterfaceType)(t.data)
	}
	return nil
}
func (t *Type) AsUnionOrIntersectionType() *UnionOrIntersectionType {
	kind := t.dataKind
	if kind == typeDataUninitialized {
		panic("uninitialized Type conversion")
	}
	if kind-typeDataUnionOrIntersectionType <= typeDataIntersectionType-typeDataUnionOrIntersectionType {
		return (*UnionOrIntersectionType)(t.data)
	}
	return nil
}
