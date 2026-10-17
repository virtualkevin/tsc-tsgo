package main

import (
	"math"
	"testing"
)

func TestWatchMemoryPolicyMatchesNativeEnvironment(t *testing.T) {
	for _, test := range []struct {
		value   string
		enabled bool
		limit   float64
	}{
		{"0", false, 0},
		{"", true, 0},
		{"-1", true, 0},
		{"invalid", true, 0},
		{"NaN", true, 0},
		{" 0 ", true, 0},
		{"0.0", true, 0},
		{"-0", true, 0},
		{"1", true, 1048576},
		{"1.5", true, 1572864},
		{" 2 ", true, 2097152},
		{"1e1", true, 10485760},
		{"0x10", true, 16777216},
		{"Infinity", true, math.Inf(1)},
	} {
		t.Run(test.value, func(t *testing.T) {
			enabled, limit := watchMemoryPolicy(test.value)
			if enabled != test.enabled || limit != test.limit {
				t.Fatalf("policy = (%v,%v), want (%v,%v)", enabled, limit, test.enabled, test.limit)
			}
		})
	}
}
