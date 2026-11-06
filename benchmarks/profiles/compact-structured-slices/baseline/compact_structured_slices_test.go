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
	d := StructuredType{properties: baselineSliceIdentity(symbols)}
	got := d.Properties()
	if unsafe.SliceData(got) != unsafe.SliceData(symbols) || cap(got) != 8 {
		t.Fatal("property header changed")
	}
	got[1] = &ast.Symbol{}
	if d.Properties()[1] != got[1] {
		t.Fatal("element alias lost")
	}
	old := d.Properties()
	d.properties = baselineSliceIdentity(append(d.properties, &ast.Symbol{}))
	if len(old) != 3 || old[:4][3] != d.Properties()[3] {
		t.Fatal("append alias lost")
	}
	copyType := d
	d.properties = baselineSliceIdentity([]*ast.Symbol(nil))
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
	d := StructuredType{signatures: baselineSliceIdentity(sigs), callSignatureCount: 1}
	if cap(d.CallSignatures()) != 1 || cap(d.ConstructSignatures()) != 2 {
		t.Fatal("public clipping changed")
	}
	if &d.CallSignatures()[0] != &sigs[0] || &d.ConstructSignatures()[0] != &sigs[1] {
		t.Fatal("public identity changed")
	}
	if cap(d.signatures[:1]) != 9 || cap(d.signatures[1:]) != 8 {
		t.Fatal("internal capacity changed")
	}
	d.signatures = baselineSliceIdentity(append(d.signatures, &Signature{}))
	if cap(d.signatures) != 9 || sigs[:4][3] != d.signatures[3] {
		t.Fatal("append reuse changed")
	}
}

func TestCompactStructuredNilAndEmpty(t *testing.T) {
	var d StructuredType
	if d.Properties() != nil || d.CallSignatures() != nil || d.ConstructSignatures() != nil || d.indexInfos != nil {
		t.Fatal("zero representation changed")
	}
	d.properties = baselineSliceIdentity([]*ast.Symbol{})
	d.signatures = baselineSliceIdentity([]*Signature{})
	d.indexInfos = baselineSliceIdentity([]*IndexInfo{})
	if d.Properties() == nil || d.CallSignatures() == nil || d.ConstructSignatures() == nil || d.indexInfos == nil {
		t.Fatal("empty representation lost")
	}
	if unsafe.Sizeof(uintptr(0)) == 8 {
		if unsafe.Sizeof(d.properties) != 24 || unsafe.Sizeof(d.signatures) != 24 || unsafe.Sizeof(d.indexInfos) != 24 {
			t.Fatal("unexpected compact header size")
		}
		t.Logf("StructuredType=%d ObjectType=%d TypeReference=%d", unsafe.Sizeof(d), unsafe.Sizeof(ObjectType{}), unsafe.Sizeof(TypeReference{}))
	}
}

func baselineSliceIdentity[T any](s []T) []T {return s}
