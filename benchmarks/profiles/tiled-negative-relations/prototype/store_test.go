package tilednegativeprototype

import (
	"math/rand/v2"
	"testing"
)

func pack(source, target uint32, state uint64) uint64 {
	return uint64(source)<<32 | uint64(target)<<2 | state
}
func TestBoundaryHistory(t *testing.T) {
	var s Store
	reference := make(map[uint64]uint32)
	ids := []uint32{1, 3, 4, 15, 16, 17, 63, 64, 65, 255, 256, (1 << 30) - 1}
	keys := []uint64{0, fallbackTag, fallbackTag | 1, 1 << 62, ^uint64(0)}
	for _, a := range ids {
		for _, b := range ids {
			for state := uint64(0); state < 4; state++ {
				keys = append(keys, pack(a, b, state))
			}
		}
	}
	// All full-width result bits, present-zero entries, replacements and transitions
	// into/out of tiles must retain exact size and value observations.
	for _, value := range []uint32{Failed, Failed, 0, 1, 2 | 8, 2 | 16, 2 | 32, 2 | 64, ^uint32(0), Failed, 0} {
		for _, key := range keys {
			s.Set(key, value)
			reference[key] = value
			if s.Size() != len(reference) {
				t.Fatal("size", key, value, s.Size(), len(reference))
			}
		}
		for _, key := range keys {
			if s.Get(key) != reference[key] {
				t.Fatal("value", key, value)
			}
		}
	}
	if len(s.tiles) != 0 || s.negativeCount != 0 {
		t.Fatal("empty tiles retained")
	}
	s = Store{}
	if s.Size() != 0 || s.Get(keys[0]) != 0 {
		t.Fatal("reset")
	}
}
func TestRandomHistories(t *testing.T) {
	for seed := uint64(1); seed <= 24; seed++ {
		rng := rand.New(rand.NewPCG(seed, seed+91))
		var s Store
		ref := make(map[uint64]uint32)
		keys := make([]uint64, 2048)
		for i := range keys {
			keys[i] = pack(uint32(rng.IntN(128)+1), uint32(rng.IntN(128)+1), uint64(rng.IntN(4)))
			if i%11 == 0 {
				keys[i] |= fallbackTag
			}
			if i%23 == 0 {
				keys[i] |= 1 << 62
			}
		}
		for step := 0; step < 16000; step++ {
			key := keys[rng.IntN(len(keys))]
			if step%3 != 0 {
				value := Failed
				if step%5 == 0 {
					value = 0
				}
				if step%7 == 0 {
					value = rng.Uint32()
				}
				s.Set(key, value)
				ref[key] = value
			} else if s.Get(key) != ref[key] {
				t.Fatal(seed, step, "read")
			}
			if s.Size() != len(ref) {
				t.Fatal(seed, step, "size")
			}
		}
		for key, value := range ref {
			if s.Get(key) != value {
				t.Fatal(seed, "final")
			}
		}
	}
}
func TestTileSharingAndIndependentStores(t *testing.T) {
	var a, b Store
	for source := uint32(16); source < 32; source++ {
		for target := uint32(16); target < 32; target++ {
			a.Set(pack(source, target, 2), Failed)
		}
	}
	if len(a.tiles) != 1 || a.Size() != 256 {
		t.Fatal("tile packing")
	}
	key := pack(16, 16, 2)
	b.Set(key, 1)
	a.Set(key, Failed|64)
	if a.Size() != 256 || a.Get(key) != 66 || b.Get(key) != 1 {
		t.Fatal("replacement/ownership")
	}
	for source := uint32(16); source < 32; source++ {
		for target := uint32(16); target < 32; target++ {
			a.Set(pack(source, target, 2), 1)
		}
	}
	if len(a.tiles) != 0 || a.Size() != 256 {
		t.Fatal("tile reclamation")
	}
}
