package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestPropertyViewCensusLifecycle(t *testing.T) {
	c, owner, original, _ := viewFixture()
	c.propertyViewCensus = new([33]uint64)
	result := &Type{flags: TypeFlagsString}
	c.valueSymbolLinks.Get(original).resolvedType = result
	v, _ := c.propertyViewOrSymbol(&owner.Type, "clone")
	c.propertyViewOrSymbol(&owner.Type, "clone")
	if v.typeOf(c, false) != result || v.typeOf(c, false) != result {
		t.Fatal("query result")
	}
	symbol := v.materialize()
	if c.getTypeOfSymbol(symbol) != result {
		t.Fatal("transfer")
	}
	counts := c.propertyViewCensus
	for index, want := range map[int]uint64{0: 2, 1: 2, 2: 0, 3: 1, 4: 4, 5: 2, 8: 1, 9: 1, 10: 1, 17: 1} {
		if counts[index] != want {
			t.Fatalf("counter %d: got %d want %d", index, counts[index], want)
		}
	}
}

func TestPropertyViewCensusEnableAndOutput(t *testing.T) {
	t.Setenv("TSC_GO_PROPERTY_VIEW_CENSUS", "")
	if newPropertyViewCensus() != nil {
		t.Fatal("disabled")
	}
	t.Setenv("TSC_GO_PROPERTY_VIEW_CENSUS", "enabled")
	c := pendingTestChecker()
	c.id = 1
	c.propertyViewCensus = newPropertyViewCensus()
	c.countPropertyView(0)
	snapshot, ok := c.PropertyViewSnapshot()
	if !ok || snapshot.Counts[0] != 1 {
		t.Fatal("snapshot")
	}
	path := filepath.Join(t.TempDir(), "counts.json")
	if err := WritePropertyViewSnapshots(path, []PropertyViewSnapshot{snapshot}); err != nil {
		t.Fatal(err)
	}
	var data struct {
		SchemaVersion int
		Categories    []string
		Owners        []PropertyViewSnapshot
	}
	raw, err := os.ReadFile(path)
	if err != nil || json.Unmarshal(raw, &data) != nil || data.SchemaVersion != 1 || len(data.Categories) != 33 || len(data.Owners) != 1 || !reflect.DeepEqual(data.Owners[0], snapshot) {
		t.Fatal("roundtrip")
	}
	if WritePropertyViewSnapshots(path, []PropertyViewSnapshot{snapshot}) == nil {
		t.Fatal("overwrote existing report")
	}
}

func TestPropertyViewBoundaryClassification(t *testing.T) {
	for index := 19; index <= 30; index++ {
		c, owner, original, _ := viewFixture()
		p := owner.pendingMembers
		name := "clone"
		resolved := owner
		switch index {
		case 19:
			resolved = nil
		case 20:
			owner.Type.symbol = c.newSymbol(ast.SymbolFlagsValueModule, "module")
		case 21:
			owner.pendingMembers = nil
		case 22:
			p.memberNames = &memberNames{}
		case 23:
			p.resolving = true
		case 24:
			p.hasBases = true
		case 25:
			p.source = nil
		case 26:
			p.source.entries = append(p.source.entries, original)
		case 27:
			name = "missing"
		case 28:
			original.Flags = ast.SymbolFlagsMethod
		case 29:
			original.CheckFlags |= ast.CheckFlagsInstantiated
		}
		before := c.SymbolCount
		if got := propertyViewBoundary(&owner.Type, resolved, name); got != index {
			t.Fatalf("boundary %d got %d", index, got)
		}
		if c.SymbolCount != before {
			t.Fatal("classification allocated symbol")
		}
	}
}

func TestPropertyViewBulkSampling(t *testing.T) {
	c := pendingTestChecker()
	c.observePropertyMaterialization(3)
	if c.propertyViewStacks != nil {
		t.Fatal("disabled sampling")
	}
	c.propertyViewCensus = new([33]uint64)
	for i := 0; i < 257; i++ {
		c.observePropertyMaterialization(3)
	}
	if c.propertyViewCensus[31] != 257 || c.propertyViewCensus[32] != 771 {
		t.Fatal("exact totals")
	}
	var samples, slots uint64
	for _, v := range c.propertyViewStacks {
		samples += v[0]
		slots += v[1]
	}
	if samples != 2 || slots != 6 {
		t.Fatal("systematic sample totals", samples, slots)
	}
}
