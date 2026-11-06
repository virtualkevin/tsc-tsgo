package core

import (
	"runtime"
	"testing"
)

func TestPointerLinkStoreInstallHistory(t *testing.T) {
	var s PointerLinkStore[int, int]
	keys := make([]*int, 1025)
	values := make([]*int, 1025)
	for i := range keys {
		if i != 0 {
			keys[i] = new(int)
			*keys[i] = i
		}
		values[i] = new(int)
		*values[i] = i + 7
		s.Install(keys[i], values[i])
	}
	runtime.GC()
	for i, k := range keys {
		if s.Get(k) != values[i] || !s.Has(k) || *s.Get(k) != i+7 {
			t.Fatal("growth lost supplied identity", i)
		}
		old := values[i]
		replacement := new(int)
		*replacement = i + 19
		s.Install(k, replacement)
		if s.Get(k) != replacement || *old != i+7 {
			t.Fatal("replacement changed published value", i)
		}
		newest := s.New(k)
		if newest == replacement || *newest != 0 || *replacement != i+19 {
			t.Fatal("New did not preserve replacement", i)
		}
	}
	if s.count != len(keys) {
		t.Fatal("replacement changed cardinality", s.count)
	}
	before := s.Get(nil)
	func() {
		defer func() {
			if recover() == nil {
				t.Error("nil install did not panic")
			}
		}()
		s.Install(nil, nil)
	}()
	if s.Get(nil) != before || s.count != len(keys) {
		t.Fatal("failed install mutated state")
	}
}
