package ast

import (
	"math/rand/v2"
	"runtime"
	"testing"
	"unsafe"
)

func TestOptionalSymbolStorageHistory(t *testing.T) {
	for seed := uint64(0); seed < 64; seed++ {
		rng := rand.New(rand.NewPCG(seed, seed+1))
		s := &Symbol{Name: "stable", Flags: SymbolFlagsProperty}
		id := GetSymbolId(s)
		values := []SymbolTable{nil, {}, {"a": s}, {"b": s}}
		targets := []*Symbol{nil, s, &Symbol{Name: "other"}}
		var members, exports SymbolTable
		var target *Symbol
		for step := 0; step < 256; step++ {
			switch rng.IntN(8) {
			case 0:
				members = values[rng.IntN(len(values))]
				s.SetMembers(members)
			case 1:
				exports = values[rng.IntN(len(values))]
				s.SetExports(exports)
			case 2:
				target = targets[rng.IntN(len(targets))]
				s.SetExportSymbol(target)
			case 3:
				if members == nil {
					members = SymbolTable{}
					values = append(values, members)
					*s.MembersSlot() = members
				}
				_ = GetMembers(s)
			case 4:
				if exports == nil {
					exports = SymbolTable{}
					values = append(values, exports)
					*s.ExportsSlot() = exports
				}
				_ = GetExports(s)
			case 5:
				if members != nil {
					members["mutable"] = targets[rng.IntN(len(targets))]
				}
			case 6:
				if exports != nil {
					exports["mutable"] = targets[rng.IntN(len(targets))]
				}
			case 7:
				if step%64 == 0 {
					runtime.GC()
				}
			}
			check := func(got, want SymbolTable) {
				t.Helper()
				if (got == nil) != (want == nil) || len(got) != len(want) {
					t.Fatalf("seed %d step %d: nil/size mismatch", seed, step)
				}
				for k, v := range want {
					if actual, ok := got[k]; !ok || actual != v {
						t.Fatal("map contents differ")
					}
				}
				if got != nil {
					marker := &Symbol{Name: "alias probe"}
					got["probe"] = marker
					if want["probe"] != marker {
						t.Fatal("map identity lost")
					}
					delete(got, "probe")
				}
			}
			check(s.MembersTable(), members)
			check(s.ExportsTable(), exports)
			if s.ExportTarget() != target || GetSymbolId(s) != id || s.Name != "stable" {
				t.Fatal("symbol identity/target changed")
			}
		}
	}
}

func TestOptionalSymbolStorageLazyAndRetainedSlots(t *testing.T) {
	s := &Symbol{}
	if s.MembersTable() != nil || s.ExportsTable() != nil || s.ExportTarget() != nil || s.cold != nil {
		t.Fatal("nonempty zero symbol")
	}
	s.SetMembers(nil)
	s.SetExports(nil)
	s.SetExportSymbol(nil)
	if s.cold != nil {
		t.Fatal("nil assignments allocate optional storage")
	}
	members := GetMembers(s)
	exports := GetExports(s)
	if members == nil || exports == nil {
		t.Fatal("lazy maps missing")
	}
	members["x"] = s
	if GetMembers(s)["x"] != s || len(exports) != 0 {
		t.Fatal("lazy maps alias each other or lose identity")
	}
	slot := s.MembersSlot()
	cold := s.cold
	replacement := SymbolTable{"new": s}
	s.SetMembers(replacement)
	s.SetExports(nil)
	s.SetExportSymbol(s)
	if slot != s.MembersSlot() || cold != s.cold || (*slot)["new"] != s || members["x"] != s {
		t.Fatal("replacement invalidates old values or slot")
	}
	s.SetMembers(nil)
	runtime.GC()
	*slot = members
	if s.MembersTable()["x"] != s || s.ExportTarget() != s {
		t.Fatal("retained slot or sibling field lost")
	}
}

func TestOptionalSymbolStorageLayout(t *testing.T) {
	if unsafe.Sizeof(uintptr(0)) == 8 && (unsafe.Sizeof(Symbol{}) != 80 || unsafe.Sizeof(symbolCold{}) != 24) {
		t.Fatalf("sizes symbol=%d cold=%d", unsafe.Sizeof(Symbol{}), unsafe.Sizeof(symbolCold{}))
	}
	t.Logf("symbol bytes=%d optional record bytes=%d", unsafe.Sizeof(Symbol{}), unsafe.Sizeof(symbolCold{}))
}
