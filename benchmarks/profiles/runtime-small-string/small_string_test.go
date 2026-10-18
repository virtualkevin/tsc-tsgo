package smallstring

import (
	"fmt"
	"strings"
	"testing"
)

func TestStringMapMutationAndMisses(t *testing.T) {
	for _, count := range []int{0, 1, 2, 3, 4, 7, 8, 9, 16, 128} {
		for _, length := range []int{0, 1, 7, 8, 15, 31, 63, 64, 65, 127} {
			t.Run(fmt.Sprintf("n%d-l%d", count, length), func(t *testing.T) {
				for trial := 0; trial < 16; trial++ {
					m := make(map[string]int)
					keys := make([]string, count)
					values := make([]int, count)
					alive := make([]bool, count)
					for i := range count {
						keys[i] = fmt.Sprintf("%04d", i) + strings.Repeat("x", length)
						values[i] = i + 1
						alive[i] = true
						m[keys[i]] = values[i]
					}
					verify := func() {
						t.Helper()
						for i, key := range keys {
							got, ok := m[key]
							want := 0
							if alive[i] {
								want = values[i]
							}
							if got != want || ok != alive[i] {
								t.Fatalf("lookup %d: %d/%v want %d/%v", i, got, ok, want, alive[i])
							}
							if _, ok := m[key+"!"]; ok {
								t.Fatal("absent key found")
							}
							if len(key) > 8 {
								other := key[:4] + "y" + key[5:]
								if _, ok := m[other]; ok {
									t.Fatal("same-length middle mismatch found")
								}
							}
						}
					}
					verify()
					for i := range keys {
						if i%2 == 0 {
							delete(m, keys[i])
							alive[i] = false
						}
					}
					verify()
					for i := range keys {
						if !alive[i] {
							values[i] += 100
							m[keys[i]] = values[i]
							alive[i] = true
						}
					}
					verify()
					clear(m)
					for i := range alive {
						alive[i] = false
					}
					verify()
				}
			})
		}
	}
}
func TestStringMapEmptyKeyAndNilValue(t *testing.T) {
	var m map[string]*int
	if _, ok := m[""]; ok {
		t.Fatal("nil map contains key")
	}
	m = map[string]*int{"": nil, "x": nil}
	for _, key := range []string{"", "x"} {
		if v, ok := m[key]; v != nil || !ok {
			t.Fatal("nil-valued entry missing")
		}
	}
	if _, ok := m["missing"]; ok {
		t.Fatal("absent entry found")
	}
}
