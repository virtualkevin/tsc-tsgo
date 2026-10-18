package core

import (
	"fmt"
	"hash/maphash"
	"runtime"
	"strings"
	"sync"
	"testing"
	"unsafe"
)

func TestStringInternerIdentityGrowthAndMembership(t *testing.T) {
	var nilTable *StringInterner
	if nilTable.Has("") || nilTable.Has("missing") {
		t.Fatal("nil table contains a key")
	}
	table := &StringInterner{}
	first := strings.Clone("repeated identifier")
	if got := table.Intern(first); unsafe.StringData(got) != unsafe.StringData(first) {
		t.Fatal("first backing string changed")
	}
	values := []string{"", "\x00", "\xff", "α", "\\u0061", "a", strings.Repeat("long", 1000)}
	for i := 0; i < 10000; i++ {
		values = append(values, fmt.Sprintf("name_%d", i))
	}
	for _, value := range values {
		table.Intern(value)
	}
	runtime.GC()
	if got := table.Intern(strings.Clone(first)); unsafe.StringData(got) != unsafe.StringData(first) {
		t.Fatal("growth replaced canonical backing string")
	}
	for _, value := range values {
		if !table.Has(value) || table.Intern(strings.Clone(value)) != value {
			t.Fatalf("lost key %q", value)
		}
	}
	if table.Has("absent") {
		t.Fatal("false membership")
	}
	// Source-file clones share the same completed table pointer.
	alias := table
	table.Intern("later")
	if !alias.Has("later") {
		t.Fatal("shared membership changed")
	}
}

func TestStringInternerCollisions(t *testing.T) {
	table := &StringInterner{seed: maphash.MakeSeed(), slots: make([]string, 64)}
	keys := []string{}
	for i := 0; len(keys) < 40; i++ {
		key := fmt.Sprint("collision_", i)
		if maphash.String(table.seed, key)&63 == 63 {
			keys = append(keys, key)
		}
	}
	for _, key := range keys {
		table.Intern(key)
	}
	for _, key := range keys {
		if !table.Has(key) {
			t.Fatal("lost colliding key")
		}
	}
	if table.Has("not present") {
		t.Fatal("false positive")
	}
	for i := 0; i < 1000; i++ {
		table.Intern(fmt.Sprint("growth_", i))
	}
	for _, key := range keys {
		if !table.Has(key) {
			t.Fatal("growth lost colliding key")
		}
	}
}

func TestStringInternerCompletedConcurrentReads(t *testing.T) {
	table := &StringInterner{}
	for _, key := range []string{"", "one", "two"} {
		table.Intern(key)
	}
	var workers sync.WaitGroup
	for i := 0; i < 8; i++ {
		workers.Go(func() {
			for j := 0; j < 1000; j++ {
				if !table.Has("one") || !table.Has("") || table.Has("missing") {
					t.Error("membership changed")
				}
			}
		})
	}
	workers.Wait()
}
