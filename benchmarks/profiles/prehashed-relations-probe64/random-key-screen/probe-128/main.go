package main

import (
	"encoding/json"
	"fmt"
	"math/rand/v2"
	"os"
)

type CacheHashKey struct{ Hi, Lo uint64 }
type RelationComparisonResult uint32

const RelationComparisonResultNone RelationComparisonResult = 0

func main() {
	encoder := json.NewEncoder(os.Stdout)
	for seed := uint64(1); seed <= 10; seed++ {
		second := uint64(0x9e3779b97f4a7c15) ^ seed
		random := rand.New(rand.NewPCG(seed, second))
		store := relationResultCache{}
		result := map[string]any{"seed1": seed, "seed2": second, "limit": 1_000_000, "fallback": false}
		for count := 1; count <= 1_000_000; count++ {
			key := CacheHashKey{Hi: random.Uint64(), Lo: random.Uint64()}
			beforeCount, beforeCapacity := store.count, len(store.keys)
			store.set(key, RelationComparisonResult(count))
			if store.count != count {
				panic("unexpected duplicate full-width key")
			}
			if store.fallback != nil {
				result["fallback"] = true
				result["attemptedInsert"] = count
				result["entriesBefore"] = beforeCount
				result["capacityBefore"] = beforeCapacity
				result["loadBefore"] = float64(beforeCount) / float64(beforeCapacity)
				result["countAfter"] = store.count
				break
			}
		}
		if store.fallback == nil {
			result["finalCount"] = store.count
			result["finalCapacity"] = len(store.keys)
		}
		if err := encoder.Encode(result); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
}
