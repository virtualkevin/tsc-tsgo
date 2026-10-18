package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"path/filepath"
	"sync"
	"testing"
)

func TestMaterializationCensusConcurrent(t *testing.T) {
	var c materializationCounts
	var wg sync.WaitGroup
	for range 8 {
		wg.Go(func() {
			for range 1000 {
				c.record(6, 3, 2)
			}
		})
	}
	wg.Wait()
	got := c.snapshot()
	if got[6] != [3]uint64{8000, 24000, 16000} {
		t.Fatal(got)
	}
	for i := range got {
		if i != 6 && got[i] != [3]uint64{} {
			t.Fatal(got)
		}
	}
}
func TestMaterializationCensusExclusiveOutput(t *testing.T) {
	var c materializationCounts
	c.record(0, 5, 0)
	path := filepath.Join(t.TempDir(), "census.json")
	if err := writeMaterializationCounts(path, &c); err != nil {
		t.Fatal(err)
	}
	before, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if !json.Valid(before) {
		t.Fatal("invalid JSON")
	}
	if err := writeMaterializationCounts(path, &c); err == nil {
		t.Fatal("overwrote evidence")
	}
	after, _ := os.ReadFile(path)
	if string(before) != string(after) {
		t.Fatal("output changed")
	}
}
func TestMaterializationCensusLifecycle(t *testing.T) {
	old := materializations
	materializations = new(materializationCounts)
	t.Cleanup(func() { materializations = old })
	c := pendingTestChecker()
	s := c.newSymbol(ast.SymbolFlagsProperty, "x")
	source := &InterfaceType{declaredMembers: ast.SymbolTable{"x": s}}
	for round := range 2 {
		p := c.pendingInstantiatedTable(source, nil)
		typ := c.newObjectType(ObjectFlagsAnonymous, nil)
		c.setPendingStructuredTypeMembers(typ, p, nil, nil, nil)
		if round == 0 {
			if len(typ.AsStructuredType().Properties()) != 1 {
				t.Fatal("properties")
			}
		}
		if len(typ.AsStructuredType().Members()) != 1 {
			t.Fatal("members")
		}
	}
	got := materializations.snapshot()
	for kind, want := range map[int]uint64{0: 2, 5: 1, 6: 1, 7: 1, 8: 1} {
		if got[kind][0] != want {
			t.Fatalf("kind %d: %v", kind, got)
		}
	}
}
