package core

import (
	"slices"
	"testing"
)

func TestFilterCapacityPreservesEmptyAndUnchanged(t *testing.T) {
	var nilInput []int
	if Filter(nilInput, func(int) bool { t.Fatal("nil callback"); return true }) != nil {
		t.Fatal("nil identity")
	}
	empty := make([]int, 0, 4)
	got := Filter(empty, func(int) bool { t.Fatal("empty callback"); return true })
	if got == nil || cap(got) != cap(empty) {
		t.Fatal("empty identity")
	}
	input := []int{1, 2, 3}
	got = Filter(input, func(int) bool { return true })
	if &got[0] != &input[0] {
		t.Fatal("unchanged slice must be reused")
	}
	got = Filter(input, func(int) bool { return false })
	if got == nil || len(got) != 0 || cap(got) != 0 {
		t.Fatal("rejected slice semantics")
	}
}

func TestFilterCapacityCallbackOrderAndPrefixSnapshot(t *testing.T) {
	input := []int{1, 2, 3, 4, 5}
	var calls []int
	got := Filter(input, func(x int) bool {
		calls = append(calls, x)
		if x == 3 {
			input[0] = 99
		}
		return x != 2 && x != 4
	})
	if !slices.Equal(calls, []int{1, 2, 3, 4, 5}) || !slices.Equal(got, []int{1, 3, 5}) {
		t.Fatalf("callbacks %v result %v", calls, got)
	}
	got[0] = 7
	if input[0] != 99 {
		t.Fatal("filtered result aliases input")
	}
}

func TestFilterCapacityMatchesReference(t *testing.T) {
	for n := 0; n <= 12; n++ {
		for mask := 0; mask < 1<<n; mask++ {
			input := make([]int, n)
			for i := range input {
				input[i] = i
			}
			var want []int
			for i := range input {
				if mask&(1<<i) != 0 {
					want = append(want, i)
				}
			}
			calls := 0
			got := Filter(input, func(x int) bool { calls++; return mask&(1<<x) != 0 })
			if !slices.Equal(got, want) || calls != n {
				t.Fatalf("n=%d mask=%d got=%v want=%v calls=%d", n, mask, got, want, calls)
			}
		}
	}
}

var filterCapacitySink []int

func TestFilterCapacityAllocations(t *testing.T) {
	input := make([]int, 128)
	for i := range input {
		input[i] = i
	}
	for _, tc := range []struct {
		name        string
		keep        func(int) bool
		allocations float64
	}{
		{"all kept", func(int) bool { return true }, 0},
		{"all rejected", func(int) bool { return false }, 0},
		{"reject first", func(x int) bool { return x != 0 }, 1},
		{"reject middle", func(x int) bool { return x != 64 }, 1},
		{"late match", func(x int) bool { return x == 127 }, 1},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got := testing.AllocsPerRun(20, func() { filterCapacitySink = Filter(input, tc.keep) })
			if got != tc.allocations {
				t.Fatalf("allocations %v want %v", got, tc.allocations)
			}
		})
	}
	filterCapacitySink = nil
}
