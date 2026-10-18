package ast

import (
	"strings"
	"sync"
	"testing"
	"unsafe"
)

func TestNameConstructionCensusMembership(t *testing.T) {
	c := &nameConstructionCensus{LimitKeys: 10, LimitBytes: 100}
	for _, kind := range []int{0, 0, 1, 2} {
		c.record(kind, "same")
	}
	c.record(0, "")
	c.record(1, "\xff\x00")
	c.record(2, "\xff\x00")
	if c.Distinct != 3 || c.DistinctBytes != 6 || c.MembershipMasks[7] != 1 || c.MembershipMasks[6] != 1 || c.MembershipMasks[1] != 1 {
		t.Fatalf("wrong membership: %+v", c)
	}
	if c.Categories[0].Requests != 3 || c.Categories[0].Distinct != 2 || c.Categories[0].NameBytes != 8 || c.Categories[0].Empty != 1 {
		t.Fatalf("wrong events: %+v", c.Categories[0])
	}
	if c.Categories[1].DistinctBytes != 6 || c.Categories[2].DistinctBytes != 6 {
		t.Fatal("wrong category bytes")
	}
}
func TestNameConstructionCensusLimits(t *testing.T) {
	c := &nameConstructionCensus{LimitKeys: 2, LimitBytes: 3}
	c.record(0, "abc")
	c.record(1, "x")
	c.record(1, "x")
	c.record(2, "")
	c.record(2, "y")
	c.record(1, "abc")
	if c.Distinct != 2 || c.DistinctBytes != 3 || c.Categories[1].Untracked != 2 || c.Categories[2].Untracked != 1 || c.MembershipMasks[3] != 1 {
		t.Fatalf("bad capped accounting: %+v", c)
	}
}
func TestNameConstructionCensusConcurrent(t *testing.T) {
	c := &nameConstructionCensus{LimitKeys: 10, LimitBytes: 100}
	var wg sync.WaitGroup
	for kind := 0; kind < 3; kind++ {
		wg.Go(func() {
			for i := 0; i < 1000; i++ {
				c.record(kind, "shared")
			}
		})
	}
	wg.Wait()
	if c.Distinct != 1 || c.MembershipMasks[7] != 1 {
		t.Fatal("shared key lost")
	}
	for _, p := range c.Categories {
		if p.Requests != 1000 || p.Distinct != 1 || p.LengthBuckets[3] != 1000 {
			t.Fatalf("lost events: %+v", p)
		}
	}
}

func TestNameConstructionCensusOwnsKeyBytes(t *testing.T) {
	c := &nameConstructionCensus{LimitKeys: 10, LimitBytes: 100}
	source := strings.Repeat("abcdefghijklmnop", 1000)
	name := source[100:120]
	c.record(0, name)
	var stored string
	for key := range c.names {
		stored = key
	}
	if unsafe.StringData(stored) == unsafe.StringData(name) {
		t.Fatal("stored key aliases source substring")
	}
	other := strings.Clone(name)
	c.record(1, other)
	for key := range c.names {
		if unsafe.StringData(key) != unsafe.StringData(stored) {
			t.Fatal("category update replaced owned key bytes")
		}
	}
}
