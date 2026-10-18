package core

import (
	"runtime"
	"testing"
)

func TestPointerFilterMembershipCollisionAndSaturation(t *testing.T) {
	var f PointerFilter[int]
	keys := make([]int, 65537)
	seen := make(map[uint64]*int)
	collided := false
	for i := range keys {
		key := &keys[i]
		h := pointerLinkHash(key) & 65535
		if previous := seen[h]; previous != nil && !collided {
			var collision PointerFilter[int]
			collision.Add(previous)
			if !collision.MayContain(key) {
				t.Fatal("same fingerprint must be a possible match")
			}
			collided = true
		}
		seen[h] = key
		f.Add(key)
	}
	if !collided {
		t.Fatal("pigeonhole collision missing")
	}
	runtime.GC()
	for i := range keys {
		if !f.MayContain(&keys[i]) {
			t.Fatal("false negative after additions/GC")
		}
	}
	f.Add(nil)
	if !f.MayContain(nil) {
		t.Fatal("nil membership")
	}
	for i := range f.bits {
		f.bits[i] = ^uint64(0)
	}
	other := new(int)
	if !f.MayContain(other) {
		t.Fatal("saturated filter must conservatively match")
	}
	runtime.KeepAlive(keys)
}

func TestPointerFilterZeroAndIndependentOwners(t *testing.T) {
	var a, b PointerFilter[int]
	key := new(int)
	if a.MayContain(key) || a.MayContain(nil) {
		t.Fatal("zero filter matched")
	}
	a.Add(key)
	a.Add(key)
	if !a.MayContain(key) || b.MayContain(key) {
		t.Fatal("ownership or repeat insertion")
	}
	runtime.KeepAlive(key)
}
