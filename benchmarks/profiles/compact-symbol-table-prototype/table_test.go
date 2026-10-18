package compact

import (
	"fmt"
	"maps"
	"math/rand/v2"
	"reflect"
	"testing"
	"unsafe"
)

func contents[V any](s Table[V]) map[string]V {
	r := make(map[string]V)
	for k, v := range s.All() {
		r[k] = v
	}
	return r
}

func TestNilAndEmpty(t *testing.T) {
	hint := -1
	if len(make(map[string]*int, hint)) != New[*int](hint).Len() {
		t.Fatal("negative runtime capacity hint")
	}
	var s Table[*int]
	if v, ok := s.Get(""); v != nil || ok {
		t.Fatal(v, ok)
	}
	s.Delete("")
	s.Clear()
	if s.Len() != 0 || s.Clone() != nil || len(contents(s)) != 0 {
		t.Fatal("nil behavior")
	}
	for range s.Values() {
		t.Fatal("nil values")
	}
	func() {
		defer func() {
			if recover() == nil {
				t.Fatal("nil write must panic")
			}
		}()
		s.Set("", nil)
	}()
	s = New[*int](0)
	s.Set("", nil)
	if v, ok := s.Get(""); v != nil || !ok || s.Len() != 1 {
		t.Fatal("present nil")
	}
	s.Delete("")
	if s == nil || s.Clone() == nil || s.Len() != 0 {
		t.Fatal("allocated empty collapsed to nil")
	}
}

func TestAliasingPromotionCloneAndKeys(t *testing.T) {
	s := New[*int](0)
	alias := s
	keys := []string{"", "\xfeindex", "\x00", "default", "__x", "é", "e\u0301", "long long long name", "ninth"}
	for i, k := range keys {
		v := i
		s.Set(k, &v)
	}
	if s.large == nil || alias.Len() != 9 {
		t.Fatal("promotion")
	}
	for i, k := range keys {
		v, ok := alias.Get(k)
		if !ok || *v != i {
			t.Fatal(k)
		}
	}
	for _, e := range s.small {
		if e.key != "" || e.value != nil {
			t.Fatal("promotion retained old pointers")
		}
	}
	c := s.Clone()
	v := 42
	c.Set(keys[0], &v)
	c.Delete(keys[1])
	if old, _ := s.Get(keys[0]); *old != 0 {
		t.Fatal("clone storage alias")
	}
	if original, _ := s.Get(keys[2]); original != func() *int { r, _ := c.Get(keys[2]); return r }() {
		t.Fatal("clone value identity")
	}
	alias.Clear()
	if s.Len() != 0 || c.Len() != 8 {
		t.Fatal("clear aliasing")
	}
}

func TestIterationMutation(t *testing.T) {
	for _, promote := range []bool{false, true} {
		t.Run(fmt.Sprint(promote), func(t *testing.T) {
			s := New[int](0)
			for i := range 8 {
				s.Set(fmt.Sprint(i), i)
			}
			seen := map[string]int{}
			first := true
			for k, v := range s.All() {
				if _, ok := seen[k]; ok {
					t.Fatal("duplicate", k)
				}
				seen[k] = v
				if first {
					first = false
					s.Delete("3")
					s.Set("4", 44)
					if promote {
						for i := 8; i < 12; i++ {
							s.Set(fmt.Sprint(i), i)
						}
					}
				}
			}
			if _, ok := seen["3"]; ok {
				t.Fatal("deleted before visit")
			}
			if seen["4"] != 44 {
				t.Fatal("replacement value")
			}
			for _, k := range []string{"0", "1", "2", "4", "5", "6", "7"} {
				if _, ok := seen[k]; !ok {
					t.Fatal("lost preexisting entry", k)
				}
			}
		})
	}
	s := New[int](0)
	s.Set("a", 1)
	s.Set("b", 2)
	n := 0
	for range s.All() {
		n++
		break
	}
	if n != 1 {
		t.Fatal("break")
	}
	n = 0
	for range s.All() {
		n++
		s.Clear()
	}
	if n != 1 {
		t.Fatal("clear during iteration")
	}
}

func TestIteratorLazyAndReentrant(t *testing.T) {
	s := New[int](0)
	it := s.Values()
	s.Set("a", 1)
	n := 0
	for v := range it {
		n += v
	}
	if n != 1 {
		t.Fatal("eager values")
	}
	for range s.All() {
		for k := range s.All() {
			s.Set(k, 2)
		}
	}
	if v, _ := s.Get("a"); v != 2 {
		t.Fatal("nested iterator")
	}
	if s.large != nil {
		t.Fatal("iteration forced map materialization")
	}
}

func TestIterationSlotReuseAndLargeMutation(t *testing.T) {
	for _, hint := range []int{0, 16} {
		s := New[int](hint)
		for i := range 8 {
			s.Set(fmt.Sprint(i), i)
		}
		seen := map[string]bool{}
		first := true
		deleted := ""
		for k := range s.All() {
			if seen[k] {
				t.Fatal("duplicate key", hint, k)
			}
			seen[k] = true
			if first {
				first = false
				deleted = "7"
				if k == deleted {
					deleted = "6"
				}
				s.Delete(deleted)
				s.Set("replacement", 99)
			}
		}
		if seen[deleted] {
			t.Fatal("deleted entry produced", hint)
		}
		for i := range 8 {
			k := fmt.Sprint(i)
			if k != deleted && !seen[k] {
				t.Fatal("surviving original entry omitted", hint, k)
			}
		}
		if hint == 0 && s.large != nil {
			t.Fatal("slot reuse promoted storage")
		}
	}
}

func TestDifferentialOperations(t *testing.T) {
	for seed := uint64(0); seed < 20; seed++ {
		r := rand.New(rand.NewPCG(seed, 17))
		s := New[int](0)
		m := map[string]int{}
		for step := range 2000 {
			k := fmt.Sprint(r.IntN(20))
			switch r.IntN(6) {
			case 0, 1:
				v := r.Int()
				s.Set(k, v)
				m[k] = v
			case 2:
				s.Delete(k)
				delete(m, k)
			case 3:
				a, ok := s.Get(k)
				b, want := m[k]
				if a != b || ok != want {
					t.Fatal(seed, step)
				}
			case 4:
				if r.IntN(20) == 0 {
					s.Clear()
					clear(m)
				}
			case 5:
				s = s.Clone()
				m = maps.Clone(m)
			}
			if s.Len() != len(m) || !reflect.DeepEqual(contents(s), m) {
				t.Fatal(seed, step)
			}
		}
	}
}

func TestLayoutEvidence(t *testing.T) {
	// Diagnostic only: no size threshold or performance conclusion.
	t.Logf("pointer-valued storage bytes=%d entry bytes=%d", unsafe.Sizeof(storage[*int]{}), unsafe.Sizeof(entry[*int]{}))
}
