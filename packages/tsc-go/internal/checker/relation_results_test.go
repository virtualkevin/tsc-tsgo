package checker

import (
	"fmt"
	"math/rand/v2"
	"slices"
	"sync"
	"testing"
)

func assertRelationResults(t *testing.T, r *Relation, want map[CacheHashKey]RelationComparisonResult) {
	t.Helper()
	if r.size() != len(want) {
		t.Fatalf("size=%d, want %d", r.size(), len(want))
	}
	for key, value := range want {
		if got := r.get(key); got != value {
			t.Fatalf("key %v: got %#x, want %#x", key, got, value)
		}
	}
}

func TestRelationResultsZeroReplacementAndIsolation(t *testing.T) {
	var relations [5]Relation
	for i := range relations {
		r := &relations[i]
		if r.size() != 0 || r.get(CacheHashKey{}) != 0 || r.results != nil {
			t.Fatal("zero relation changed during read")
		}
		for _, value := range []RelationComparisonResult{0, RelationComparisonResultSucceeded, RelationComparisonResultFailed | RelationComparisonResultOverflow | RelationComparisonResultReportsMask, ^RelationComparisonResult(0), 0, RelationComparisonResult(i + 1)} {
			r.set(CacheHashKey{}, value)
			if r.size() != 1 || r.get(CacheHashKey{}) != value {
				t.Fatal("zero-key replacement lost value bits or changed count")
			}
		}
	}
	for i := range relations {
		if relations[i].get(CacheHashKey{}) != RelationComparisonResult(i+1) {
			t.Fatal("relation stores are not isolated")
		}
	}
	relations[0].results = nil
	if relations[0].size() != 0 || relations[0].get(CacheHashKey{}) != 0 {
		t.Fatal("nil reset retained count or contents")
	}
	relations[0].set(CacheHashKey{}, 0)
	if relations[0].size() != 1 {
		t.Fatal("explicit zero after reset did not count")
	}
}

func TestRelationResultsDifferential(t *testing.T) {
	for _, collide := range []bool{false, true} {
		t.Run(fmt.Sprintf("collide%t", collide), func(t *testing.T) {
			random := rand.New(rand.NewPCG(17, 31))
			keys := make([]CacheHashKey, max(512, relationResultProbeLimit+64))
			for i := range keys {
				keys[i] = CacheHashKey{Hi: uint64(i), Lo: random.Uint64()}
				if collide {
					keys[i].Lo = 0
				}
			}
			keys[0] = CacheHashKey{}
			var r Relation
			want := make(map[CacheHashKey]RelationComparisonResult)
			for i := 0; i < 5000; i++ {
				key := keys[random.IntN(len(keys))]
				value := RelationComparisonResult(random.Uint32())
				if i%7 == 0 {
					value = 0
				}
				r.set(key, value)
				want[key] = value
				probe := keys[random.IntN(len(keys))]
				if r.size() != len(want) || r.get(probe) != want[probe] {
					t.Fatalf("operation %d disagrees with map", i)
				}
			}
			assertRelationResults(t, &r, want)
			if (r.results.fallback != nil) != collide {
				t.Fatal("expected table/fallback coverage not reached")
			}
			missing := CacheHashKey{Hi: ^uint64(0), Lo: 0}
			if r.get(missing) != 0 {
				t.Fatal("missing full key matched another key's bucket")
			}
		})
	}
}

func TestRelationResultsOverwriteBeforeGrowth(t *testing.T) {
	var r Relation
	for i := 0; i < 6; i++ {
		r.set(CacheHashKey{Lo: uint64(i)}, RelationComparisonResult(i))
	}
	keys := &r.results.keys[0]
	for i := 0; i < 6; i++ {
		r.set(CacheHashKey{Lo: uint64(i)}, ^RelationComparisonResult(0))
	}
	if len(r.results.keys) != 8 || &r.results.keys[0] != keys || r.size() != 6 {
		t.Fatal("replacement grew or replaced the backing table")
	}
	r.set(CacheHashKey{Lo: 6}, 0)
	if len(r.results.keys) != 16 || r.size() != 7 {
		t.Fatal("new entry did not grow at the load threshold")
	}
	for i := 0; i < 6; i++ {
		if r.get(CacheHashKey{Lo: uint64(i)}) != ^RelationComparisonResult(0) {
			t.Fatal("growth lost an overwritten result")
		}
	}
}

func TestRelationResultsProbeFallback(t *testing.T) {
	var r Relation
	want := make(map[CacheHashKey]RelationComparisonResult)
	for i := 0; i < relationResultProbeLimit; i++ {
		key := CacheHashKey{Hi: uint64(i), Lo: ^uint64(0)}
		value := RelationComparisonResult(i)
		r.set(key, value)
		want[key] = value
	}
	if r.results.fallback != nil || r.get(CacheHashKey{Hi: 1000, Lo: ^uint64(0)}) != 0 {
		t.Fatal("bounded full-chain miss did not remain a read-only table lookup")
	}
	// The final key is at the final permitted probe distance. Replacement must find it before
	// considering exhaustion or growth, and must retain table mode/count.
	last := CacheHashKey{Hi: relationResultProbeLimit - 1, Lo: ^uint64(0)}
	capacity := len(r.results.keys)
	backing := &r.results.keys[0]
	r.set(last, ^RelationComparisonResult(0))
	want[last] = ^RelationComparisonResult(0)
	if r.results.fallback != nil || len(r.results.keys) != capacity || &r.results.keys[0] != backing {
		t.Fatal("last-probe overwrite grew the table or triggered fallback")
	}
	assertRelationResults(t, &r, want)
	key := CacheHashKey{Hi: 1000, Lo: ^uint64(0)}
	r.set(key, 0)
	want[key] = 0
	if r.results.fallback == nil || r.results.keys != nil || r.results.values != nil || r.results.occupied != nil {
		t.Fatal("probe exhaustion did not permanently replace table storage")
	}
	assertRelationResults(t, &r, want)
	r.set(key, ^RelationComparisonResult(0))
	want[key] = ^RelationComparisonResult(0)
	assertRelationResults(t, &r, want)
	// Existing private callers reset results directly. This must discard a
	// fallback map just as completely as it discards table storage.
	r.results = nil
	if r.size() != 0 || r.get(last) != 0 || r.get(key) != 0 || r.results != nil {
		t.Fatal("fallback reset retained contents/count or allocated during read")
	}
	r.set(CacheHashKey{}, 0)
	if r.size() != 1 || r.results.fallback != nil || len(r.results.keys) != relationResultInitialCapacity {
		t.Fatal("reinsert after fallback reset did not create a fresh small table")
	}
	if r.get(last) != 0 || r.get(key) != 0 {
		t.Fatal("fallback reset leaked old entries into new table")
	}
}

func TestRelationResultsRehashFallback(t *testing.T) {
	// Production only doubles capacity. A controlled smaller destination makes
	// formerly separated buckets collide, exercising both transactional failure
	// branches without assuming real-world doubling can trigger either one.
	for _, count := range []int{relationResultProbeLimit, relationResultProbeLimit + 1} {
		t.Run(fmt.Sprintf("entries%d", count), func(t *testing.T) {
			store := newRelationResultTable(relationResultProbeLimit * 4)
			r := Relation{results: &store}
			want := make(map[CacheHashKey]RelationComparisonResult)
			for i := 0; i < count; i++ {
				key := CacheHashKey{Hi: uint64(i), Lo: uint64(i * relationResultProbeLimit * 2)}
				value := RelationComparisonResult(i)
				r.set(key, value)
				want[key] = value
			}
			oldKeys, oldValues, oldOccupied := store.keys, store.values, store.occupied
			keysCopy, valuesCopy, occupiedCopy := slices.Clone(oldKeys), slices.Clone(oldValues), slices.Clone(oldOccupied)
			pending := CacheHashKey{Hi: 9999}
			store.rebuild(relationResultProbeLimit*2, pending, RelationComparisonResultOverflow)
			want[pending] = RelationComparisonResultOverflow
			if store.fallback == nil {
				t.Fatal("forced rehash collision did not fall back")
			}
			assertRelationResults(t, &r, want)
			if !slices.Equal(oldKeys, keysCopy) || !slices.Equal(oldValues, valuesCopy) || !slices.Equal(oldOccupied, occupiedCopy) {
				t.Fatal("failed rehash mutated original backing arrays")
			}
		})
	}
}

func TestRelationResultsReadOnlyConcurrency(t *testing.T) {
	for _, collide := range []bool{false, true} {
		t.Run(fmt.Sprintf("collide%t", collide), func(t *testing.T) {
			var r Relation
			keys := make([]CacheHashKey, max(256, relationResultProbeLimit+1))
			for i := range keys {
				keys[i] = CacheHashKey{Hi: uint64(i), Lo: uint64(i)}
				if collide {
					keys[i].Lo = 0
				}
				r.set(keys[i], RelationComparisonResult(i))
			}
			var readers sync.WaitGroup
			for range 8 {
				readers.Go(func() {
					for range 20 {
						for i, key := range keys {
							if r.get(key) != RelationComparisonResult(i) || r.size() != len(keys) {
								t.Error("populated read disagrees")
								return
							}
						}
						if r.get(CacheHashKey{Hi: ^uint64(0)}) != 0 {
							t.Error("missing read disagrees")
						}
					}
				})
			}
			readers.Wait()
		})
	}
}

func TestRelationResultsCheckedCapacity(t *testing.T) {
	for _, capacity := range []int{-1, 0, 1, 7, 9, int(^uint(0) >> 1)} {
		if _, ok := nextRelationResultCapacity(capacity); ok {
			t.Fatalf("accepted invalid capacity %d", capacity)
		}
	}
	capacity := relationResultInitialCapacity
	for {
		next, ok := nextRelationResultCapacity(capacity)
		if !ok {
			if capacity <= int(^uint(0)>>1)/16/2 {
				t.Fatal("rejected safe power-of-two doubling")
			}
			break
		}
		if next != capacity*2 || next <= capacity || next > int(^uint(0)>>1)/16 {
			t.Fatal("capacity check overflowed")
		}
		capacity = next
	}
}
