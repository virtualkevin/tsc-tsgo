package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"runtime"
	"slices"
	"testing"
	"unsafe"
)

func TestCompactStructuredSliceAliases(t *testing.T) {
	symbols := make([]*ast.Symbol, 3, 8)
	for i := range symbols {
		symbols[i] = &ast.Symbol{}
	}
	d := StructuredType{properties: compactSliceFrom(symbols)}
	got := d.Properties()
	if unsafe.SliceData(got) != unsafe.SliceData(symbols) || cap(got) != 8 {
		t.Fatal("property header changed")
	}
	got[1] = &ast.Symbol{}
	if d.Properties()[1] != got[1] {
		t.Fatal("element alias lost")
	}
	old := d.Properties()
	d.properties = compactSliceFrom(append(d.properties.Values(), &ast.Symbol{}))
	if len(old) != 3 || old[:4][3] != d.Properties()[3] {
		t.Fatal("append alias lost")
	}
	copyType := d
	d.properties = compactSliceFrom([]*ast.Symbol(nil))
	runtime.GC()
	if !slices.Equal(copyType.Properties()[:3], old) {
		t.Fatal("copied owner invalidated")
	}
}

func TestCompactStructuredSignatureCapacity(t *testing.T) {
	sigs := make([]*Signature, 3, 9)
	for i := range sigs {
		sigs[i] = &Signature{}
	}
	d := StructuredType{signatures: compactSliceFrom(sigs), callSignatureCount: 1}
	if cap(d.CallSignatures()) != 1 || cap(d.ConstructSignatures()) != 2 {
		t.Fatal("public clipping changed")
	}
	if &d.CallSignatures()[0] != &sigs[0] || &d.ConstructSignatures()[0] != &sigs[1] {
		t.Fatal("public identity changed")
	}
	if cap(d.signatures.Values()[:1]) != 9 || cap(d.signatures.Values()[1:]) != 8 {
		t.Fatal("internal capacity changed")
	}
	d.signatures = compactSliceFrom(append(d.signatures.Values(), &Signature{}))
	if cap(d.signatures.Values()) != 9 || sigs[:4][3] != d.signatures.Values()[3] {
		t.Fatal("append reuse changed")
	}
}

func TestCompactStructuredNilAndEmpty(t *testing.T) {
	var d StructuredType
	if d.Properties() != nil || d.CallSignatures() != nil || d.ConstructSignatures() != nil || d.indexInfos.Values() != nil {
		t.Fatal("zero representation changed")
	}
	d.properties = compactSliceFrom([]*ast.Symbol{})
	d.signatures = compactSliceFrom([]*Signature{})
	d.indexInfos = compactSliceFrom([]*IndexInfo{})
	if d.Properties() == nil || d.CallSignatures() == nil || d.ConstructSignatures() == nil || d.indexInfos.Values() == nil {
		t.Fatal("empty representation lost")
	}
	if unsafe.Sizeof(uintptr(0)) == 8 {
		if unsafe.Sizeof(d.properties) != 16 || unsafe.Sizeof(d.signatures) != 16 || unsafe.Sizeof(d.indexInfos) != 16 {
			t.Fatal("unexpected compact header size")
		}
		t.Logf("StructuredType=%d ObjectType=%d TypeReference=%d", unsafe.Sizeof(d), unsafe.Sizeof(ObjectType{}), unsafe.Sizeof(TypeReference{}))
	}
}
