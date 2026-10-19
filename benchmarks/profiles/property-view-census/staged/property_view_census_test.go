package checker

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestPropertyViewCensusLifecycle(t *testing.T) {
	c, owner, original, _ := viewFixture()
	c.propertyViewCensus = new([19]uint64)
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
	if err != nil || json.Unmarshal(raw, &data) != nil || data.SchemaVersion != 1 || len(data.Categories) != 19 || len(data.Owners) != 1 || data.Owners[0] != snapshot {
		t.Fatal("roundtrip")
	}
	if WritePropertyViewSnapshots(path, []PropertyViewSnapshot{snapshot}) == nil {
		t.Fatal("overwrote existing report")
	}
}
