package compactslice

import (
	"math/rand/v2"
	"runtime"
	"slices"
	"strconv"
	"sync"
	"testing"
	"unsafe"
	"weak"
)

func same[T comparable](t *testing.T, got, want []T) {
	t.Helper()
	if (got == nil) != (want == nil) || len(got) != len(want) || cap(got) != cap(want) || unsafe.SliceData(got) != unsafe.SliceData(want) || !slices.Equal(got, want) {
		t.Fatal("header, identity or elements changed")
	}
}

func TestHeaderRoundTrip(t *testing.T) {
	var zero Slice[int]
	same(t, zero.Values(), []int(nil))
	a := make([]int, 24)
	for i := range a {
		a[i] = i
	}
	for _, s := range [][]int{nil, {}, make([]int, 0, 12), a, a[4:11], a[4:11:15], a[:0], a[24:24]} {
		same(t, From(s).Values(), s)
	}
	if strconv.IntSize == 64 && unsafe.Sizeof(Slice[int]{}) != 16 {
		t.Fatal("expected 16-byte amd64 header")
	}
}

func TestAliasingAndAppend(t *testing.T) {
	a := make([]int, 4, 8)
	c := From(a)
	saved := c
	v := c.Values()
	v[2] = 99
	if a[2] != 99 {
		t.Fatal("lost element alias")
	}
	v = append(v, 7)
	c = From(v)
	if len(saved.Values()) != 4 || saved.Values()[:5][4] != 7 {
		t.Fatal("lost old-header/backing alias")
	}
	old := c.Values()
	v = append(v, 1, 2, 3, 4, 5, 6)
	c = From(v)
	if unsafe.SliceData(old) == unsafe.SliceData(c.Values()) {
		t.Fatal("append should have grown")
	}
	old[0] = 123
	if c.Values()[0] == 123 {
		t.Fatal("grown array aliases old array")
	}
	c = Slice[int]{}
	if saved.Values()[0] != 123 {
		t.Fatal("copy invalidated on replacement")
	}
}

func TestRandomHeaderHistories(t *testing.T) {
	for seed := uint64(1); seed <= 128; seed++ {
		r := rand.New(rand.NewPCG(seed, seed+19))
		var s []int
		var c Slice[int]
		for step := 0; step < 1024; step++ {
			switch r.IntN(5) {
			case 0:
				s = append(c.Values(), step)
			case 1:
				v := c.Values()
				lo := r.IntN(len(v) + 1)
				hi := lo + r.IntN(len(v)-lo+1)
				limit := hi + r.IntN(cap(v)-hi+1)
				s = v[lo:hi:limit]
			case 2:
				s = nil
			case 3:
				s = make([]int, r.IntN(16), 32)
			case 4:
				s = c.Values()
				if len(s) > 0 {
					s[r.IntN(len(s))] = step
				}
			}
			c = From(s)
			same(t, c.Values(), s)
		}
	}
}

func TestPackingAndLargeSlices(t *testing.T) {
	max := uint64(^uint32(0))
	for _, n := range []uint64{0, 1, max - 1, max, max + 1, ^uint64(0)} {
		for _, cap := range []uint64{0, 1, max - 1, max, max + 1, ^uint64(0)} {
			shape, ok := pack(n, cap)
			want := n <= cap && cap <= max && !(n == max && cap == max)
			if ok != want {
				t.Fatal("domain mismatch", n, cap)
			}
			if ok && (uint64(uint32(shape)) != n || shape>>32 != cap) {
				t.Fatal("packing mismatch")
			}
		}
	}
	if strconv.IntSize != 64 {
		return
	}
	// Zero-sized elements let us test actual multi-billion-element headers
	// without allocating multi-gigabyte backing storage or forging a header.
	for _, n := range []uint64{max, max + 1, max + 7} {
		s := make([]struct{}, int(n))
		c := From(s)
		if c.shape != indirectShape {
			t.Fatal("missing indirect fallback")
		}
		v := c.Values()
		if len(v) != len(s) || cap(v) != cap(s) || unsafe.SliceData(v) != unsafe.SliceData(s) {
			t.Fatal("large header changed")
		}
		shortened := From(v[:3])
		if (shortened.shape == indirectShape) != (n > max) || len(shortened.Values()) != 3 || cap(shortened.Values()) != len(s) {
			t.Fatal("large capacity lost")
		}
	}
}

type payload struct {
	n       int
	padding [4096]byte
}

//go:noinline
func retained() (Slice[*payload], weak.Pointer[payload]) {
	p := &payload{n: 73}
	s := make([]*payload, 3, 7)
	s[2] = p
	return From(s[1:3]), weak.Make(p)
}
func TestRetainedBackingGraph(t *testing.T) {
	c, w := retained()
	copyHeader := c
	c = Slice[*payload]{}
	for range 4 {
		runtime.GC()
	}
	if w.Value() == nil || copyHeader.Values()[1].n != 73 {
		t.Fatal("backing graph collected")
	}
	copyHeader.Values()[1].n = 91
	if w.Value().n != 91 {
		t.Fatal("identity lost")
	}
	runtime.KeepAlive(copyHeader)
}

func TestConcurrentPublishedReads(t *testing.T) {
	c := From([]int{1, 2, 3, 4})
	var wg sync.WaitGroup
	for range 8 {
		wg.Go(func() {
			for range 10000 {
				v := c.Values()
				if v[2] != 3 || cap(v) != 4 {
					t.Error("read mismatch")
					return
				}
			}
		})
	}
	wg.Wait()
}
