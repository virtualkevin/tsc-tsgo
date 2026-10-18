package checker

import (
	"runtime"
	"testing"
	"unsafe"
)

func TestStructuredCallDataEmptyAndAliasing(t *testing.T) {
	c := pendingTestChecker()
	typ := c.newObjectType(ObjectFlagsAnonymous, nil)
	d := typ.AsStructuredType()
	c.setStructuredTypeMembers(typ, nil, nil, nil, nil)
	if d.callData != nil || d.CallSignatures() != nil || d.ConstructSignatures() != nil || d.indexInfoList() != nil {
		t.Fatal("empty members changed zero values or allocated storage")
	}
	// Non-nil empty index information must stay distinct from nil.
	empty := make([]*IndexInfo, 0, 3)
	c.setStructuredTypeMembers(typ, nil, nil, nil, empty)
	if d.indexInfoList() == nil || cap(d.indexInfoList()) != 0 {
		t.Fatal("empty index information lost nil/capacity semantics")
	}
	calls := make([]*Signature, 1, 4)
	calls[0] = &Signature{id: 7}
	c.setStructuredTypeMembers(typ, nil, calls, nil, nil)
	if d.CallSignatures()[0] != calls[0] || cap(d.CallSignatures()) != 1 {
		t.Fatal("call identity or clipped capacity changed")
	}
	calls[0] = &Signature{id: 8}
	if d.CallSignatures()[0] != calls[0] {
		t.Fatal("backing slice alias was lost")
	}
	ctors := []*Signature{{id: 9}}
	c.setStructuredTypeMembers(typ, nil, calls, ctors, nil)
	if len(d.CallSignatures()) != 1 || d.ConstructSignatures()[0] != ctors[0] || cap(d.ConstructSignatures()) != 1 {
		t.Fatal("call/construct partition changed")
	}
	cached := &Type{flags: TypeFlagsString}
	d.setWithoutAbstractConstructSignatures(cached)
	c.setStructuredTypeMembers(typ, nil, nil, nil, nil)
	if d.CallSignatures() != nil || d.ConstructSignatures() != nil || d.indexInfoList() != nil || d.withoutAbstractConstructSignatures() != cached {
		t.Fatal("reset changed independently cached emit type")
	}
}

func TestStructuredCallDataRetainsTargets(t *testing.T) {
	d := &StructuredType{}
	d.setSignatureList([]*Signature{{id: 11}}, 1)
	d.setIndexInfoList([]*IndexInfo{{}})
	d.setWithoutAbstractConstructSignatures(&Type{flags: TypeFlagsNumber})
	runtime.GC()
	if d.CallSignatures()[0].id != 11 || d.indexInfoList()[0] == nil || d.withoutAbstractConstructSignatures().flags != TypeFlagsNumber {
		t.Fatal("owned data lost reachable targets")
	}
	runtime.KeepAlive(d)
}

func TestStructuredCallDataLayout(t *testing.T) {
	t.Logf("StructuredType=%d ObjectType=%d TypeReference=%d UnionType=%d cold=%d", unsafe.Sizeof(StructuredType{}), unsafe.Sizeof(ObjectType{}), unsafe.Sizeof(TypeReference{}), unsafe.Sizeof(UnionType{}), unsafe.Sizeof(structuredCallData{}))
}
