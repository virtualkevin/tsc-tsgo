package graph

import (
	"math"
	"math/rand"
	"reflect"
	"runtime"
	"sync"
	"testing"
)

type modelRecord struct {
	value Value
	edges [4]uint32
}

func TestStatefulGraphAgainstIndependentModel(t *testing.T) {
	g := New(4096)
	refs := []Ref{{}}
	model := []modelRecord{{}}
	rng := rand.New(rand.NewSource(17429))
	for step := 0; step < 65536; step++ {
		var children [4]Ref
		var ids [4]uint32
		for i := range children {
			n := rng.Intn(len(refs))
			children[i] = refs[n]
			ids[i] = uint32(n)
		}
		value := Value{rng.Uint32(), rng.Uint64()}
		if len(refs) == 1 || (len(refs) <= 4096 && rng.Intn(4) == 0) {
			r, err := g.Add(value, children)
			if err != nil {
				t.Fatal(err)
			}
			if r.ID() != uint32(len(refs)) {
				t.Fatal("identity changed")
			}
			refs = append(refs, r)
			model = append(model, modelRecord{value, ids})
		} else {
			n := 1 + rng.Intn(len(refs)-1)
			if err := g.Set(refs[n], value, children); err != nil {
				t.Fatal(err)
			}
			model[n] = modelRecord{value, ids}
		}
		n := 1 + rng.Intn(len(refs)-1)
		v, edges, ok := refs[n].Read()
		if !ok || v != model[n].value {
			t.Fatal("value mismatch", step, n)
		}
		for i, e := range edges {
			if e != refs[model[n].edges[i]] {
				t.Fatal("edge identity mismatch", step, n, i)
			}
		}
	}
	for n := 1; n < len(refs); n++ {
		v, edges, ok := refs[n].Read()
		if !ok || v != model[n].value {
			t.Fatal(n)
		}
		for i, e := range edges {
			if e != refs[model[n].edges[i]] {
				t.Fatal(n, i)
			}
		}
	}
}

func TestOwnerAndExhaustionFailuresAreAtomic(t *testing.T) {
	a, b := New(1), New(1)
	ra, _ := a.Add(Value{1, 2}, [4]Ref{})
	rb, _ := b.Add(Value{3, 4}, [4]Ref{})
	if ra == rb || ra.ID() != rb.ID() {
		t.Fatal("owner identity not represented")
	}
	before, _, _ := ra.Read()
	slots := a.AllocatedSlots()
	if _, err := a.Add(Value{}, [4]Ref{}); err != ErrFull {
		t.Fatal(err)
	}
	if err := a.Set(ra, Value{}, [4]Ref{rb}); err != ErrOwner {
		t.Fatal(err)
	}
	if err := a.Set(rb, Value{}, [4]Ref{}); err != ErrOwner {
		t.Fatal(err)
	}
	for _, bad := range []Ref{{a, 0}, {nil, 1}, {a, 2}} {
		if err := a.Set(ra, Value{}, [4]Ref{bad}); err != ErrOwner {
			t.Fatal(err)
		}
	}
	after, _, _ := ra.Read()
	if before != after || a.Len() != 1 || a.AllocatedSlots() != slots {
		t.Fatal("failure mutated graph")
	}
	zero := New(0)
	if _, err := zero.Add(Value{}, [4]Ref{}); err != ErrFull || zero.AllocatedSlots() != 0 {
		t.Fatal("zero capacity")
	}
	// Exercise the exhaustion check at its actual uint32 boundary without allocating
	// billions of records. No slot access is permitted on this deliberately full sentinel.
	max := &Graph{count: math.MaxUint32, limit: math.MaxUint32}
	if _, err := max.Add(Value{}, [4]Ref{}); err != ErrFull || max.count != math.MaxUint32 {
		t.Fatal("overflow")
	}
	if _, _, ok := (Ref{}).Read(); ok {
		t.Fatal("nil reference readable")
	}
}

// Returning only a Ref must retain the owner, all pages, and edges to distant pages.
func retainedRoot(t *testing.T) Ref {
	g := New(10000)
	first, _ := g.Add(Value{1, 17}, [4]Ref{})
	last := first
	for i := uint32(1); i < 8193; i++ {
		var err error
		last, err = g.Add(Value{i, uint64(i)}, [4]Ref{last, first})
		if err != nil {
			t.Fatal(err)
		}
	}
	if err := g.Set(first, Value{1, 99}, [4]Ref{last}); err != nil {
		t.Fatal(err)
	}
	return last
}
func TestPublishedRefRetainsPagesAcrossGCAndGrowth(t *testing.T) {
	root := retainedRoot(t)
	for range 4 {
		runtime.GC()
	}
	v, edges, ok := root.Read()
	if !ok || v.Kind != 8192 {
		t.Fatal("root lost")
	}
	first, cycle, ok := edges[1].Read()
	if !ok || first.Payload != 99 || cycle[0] != root {
		t.Fatal("old page or cycle lost")
	}
	n := 0
	for cur := root; !cur.IsNil() && n < 8193; n++ {
		_, edges, ok := cur.Read()
		if !ok {
			t.Fatal("chain lost", n)
		}
		if edges[1].IsNil() {
			break
		}
		cur = edges[0]
	}
	if n != 8192 {
		t.Fatal("chain length", n)
	}
	runtime.KeepAlive(root)
}

func TestConcurrentCompletedReads(t *testing.T) {
	g := New(1)
	r, _ := g.Add(Value{2, 7}, [4]Ref{})
	if err := g.Set(r, Value{2, 7}, [4]Ref{r}); err != nil {
		t.Fatal(err)
	}
	var wg sync.WaitGroup
	for range 8 {
		wg.Go(func() {
			for range 4096 {
				v, edges, ok := r.Read()
				if !ok || v.Payload != 7 || edges[0] != r {
					t.Error("read changed")
					return
				}
			}
		})
	}
	wg.Wait()
}

func TestLayoutAndHandleBoundaries(t *testing.T) {
	typ := reflect.TypeOf(record{})
	var check func(reflect.Type)
	check = func(x reflect.Type) {
		switch x.Kind() {
		case reflect.Struct:
			for i := 0; i < x.NumField(); i++ {
				check(x.Field(i).Type)
			}
		case reflect.Array:
			check(x.Elem())
		case reflect.Uint32, reflect.Uint64:
		default:
			t.Fatal("pointer-bearing or unexpected record field", x)
		}
	}
	check(typ)
	for _, h := range []uint32{1, 255, 256, 257, 65535, 65536, math.MaxUint32} {
		index := h - 1
		page, slot := index>>pageBits, index&pageMask
		if (uint64(page)<<pageBits)+uint64(slot)+1 != uint64(h) || slot >= pageSize {
			t.Fatal(h)
		}
	}
	t.Logf("record=%d page=%d publishedRef=%d graph=%d", typ.Size(), reflect.TypeOf(page{}).Size(), reflect.TypeOf(Ref{}).Size(), reflect.TypeOf(Graph{}).Size())
}
