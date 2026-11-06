package graph

import (
	"errors"
	"math/rand/v2"
	"reflect"
	"runtime"
	"sync"
	"testing"
	"unsafe"
	"weak"
)

func add(t *testing.T, g *Graph, v Value, edges [4]Ref) Ref {
	t.Helper()
	r, e := g.Add(v, edges)
	if e != nil {
		t.Fatal(e)
	}
	return r
}
func audit(t *testing.T, p *page) {
	t.Helper()
	counts := make(map[*page]int)
	for i := range int(p.used) {
		_, edges, ok := (Ref{p, uint16(i)}).Read()
		if !ok {
			t.Fatal("invalid used slot")
		}
		for _, r := range edges {
			if !r.IsNil() && r.page != p {
				counts[r.page]++
			}
		}
	}
	if len(counts) != len(p.index) {
		t.Fatal("index cardinality")
	}
	free := make(map[uint16]bool)
	for _, i := range p.free {
		if free[i] || int(i) >= len(p.remote) {
			t.Fatal("invalid free slot")
		}
		free[i] = true
	}
	for i, e := range p.remote {
		if e.count == 0 {
			if e.target != nil || !free[uint16(i)] {
				t.Fatal("dead edge retains target")
			}
			continue
		}
		if e.target == nil || free[uint16(i)] || counts[e.target] != int(e.count) || p.index[e.target] != uint16(i) {
			t.Fatal("remote reference accounting")
		}
	}
}
func TestStatefulGraphAgreement(t *testing.T) {
	type expected struct {
		v     Value
		edges [4]uint32
	}
	g := New(4096)
	refs := []Ref{}
	model := []expected{}
	rng := rand.New(rand.NewPCG(81, 209))
	for step := range 32768 {
		var edges [4]Ref
		var ids [4]uint32
		for i := range edges {
			if len(refs) > 0 && rng.IntN(4) != 0 {
				n := rng.IntN(len(refs))
				edges[i] = refs[n]
				ids[i] = uint32(n + 1)
			}
		}
		v := Value{uint32(step % 17), uint64(step)}
		if len(refs) < 4096 && (len(refs) == 0 || rng.IntN(3) == 0) {
			r := add(t, g, v, edges)
			refs = append(refs, r)
			model = append(model, expected{v, ids})
			if r.ID() != uint32(len(refs)) {
				t.Fatal("ID sequence")
			}
		} else {
			n := rng.IntN(len(refs))
			if e := g.Set(refs[n], v, edges); e != nil {
				t.Fatal(e)
			}
			model[n] = expected{v, ids}
		}
		n := rng.IntN(len(refs))
		got, es, ok := refs[n].Read()
		if !ok || got != model[n].v {
			t.Fatal("value mismatch", step)
		}
		for i, r := range es {
			if r.ID() != model[n].edges[i] || (!r.IsNil() && r != refs[r.ID()-1]) {
				t.Fatal("edge identity mismatch", step)
			}
		}
		if step%256 == 0 {
			seen := map[*page]bool{}
			for _, r := range refs {
				if !seen[r.page] {
					audit(t, r.page)
					seen[r.page] = true
				}
			}
		}
	}
	runtime.GC()
	for n, r := range refs {
		v, es, ok := r.Read()
		if !ok || v != model[n].v {
			t.Fatal("final value")
		}
		for i, e := range es {
			if e.ID() != model[n].edges[i] {
				t.Fatal("final edge")
			}
		}
	}
}
func TestOwnershipAndFailureAtomicity(t *testing.T) {
	g := New(2)
	a := add(t, g, Value{1, 2}, [4]Ref{})
	b := add(t, g, Value{3, 4}, [4]Ref{a})
	other := add(t, New(1), Value{}, [4]Ref{})
	before := g.count
	v, edges, _ := b.Read()
	for _, bad := range []Ref{other, {nil, 1}, {a.page, 256}} {
		if !errors.Is(g.Set(b, Value{}, [4]Ref{a, bad}), ErrOwner) {
			t.Fatal("foreign edge admitted")
		}
		if !errors.Is(g.Set(bad, Value{}, [4]Ref{}), ErrOwner) {
			t.Fatal("foreign target admitted")
		}
		if _, err := g.Add(Value{}, [4]Ref{bad}); !errors.Is(err, ErrOwner) {
			t.Fatal("foreign add admitted")
		}
		got, es, _ := b.Read()
		if got != v || es != edges || g.count != before {
			t.Fatal("failed mutation changed state")
		}
	}
	if _, e := g.Add(Value{}, [4]Ref{}); !errors.Is(e, ErrFull) {
		t.Fatal("capacity")
	}
	if _, e := New(0).Add(Value{}, [4]Ref{}); !errors.Is(e, ErrFull) {
		t.Fatal("zero capacity")
	}
	full := New(^uint32(0))
	full.count = full.limit
	if _, e := full.Add(Value{}, [4]Ref{}); !errors.Is(e, ErrFull) || full.current != nil {
		t.Fatal("uint32 full boundary")
	}
	if _, _, ok := (Ref{}).Read(); ok {
		t.Fatal("nil read")
	}
}
func TestRemoteCapacityAndReuse(t *testing.T) {
	g := New(300000)
	source := make([]Ref, pageSize)
	for i := range source {
		source[i] = add(t, g, Value{}, [4]Ref{})
	}
	targets := make([]Ref, maxRemoteSlots+4)
	for i := range targets {
		targets[i] = add(t, g, Value{Payload: uint64(i)}, [4]Ref{})
		for range pageSize - 1 {
			add(t, g, Value{}, [4]Ref{})
		}
	}
	for i, r := range source {
		var edges [4]Ref
		copy(edges[:], targets[4*i:4*i+4])
		if e := g.Set(r, Value{}, edges); e != nil {
			t.Fatal(e)
		}
	}
	p := source[0].page
	audit(t, p)
	if len(p.remote) != maxRemoteSlots {
		t.Fatal("capacity fixture")
	}
	var next [4]Ref
	copy(next[:], targets[maxRemoteSlots:])
	if e := g.Set(source[0], Value{}, next); e != nil {
		t.Fatal(e)
	}
	audit(t, p)
	if len(p.remote) != maxRemoteSlots || len(p.free) != 0 {
		t.Fatal("free slots were not reused")
	}
	for _, r := range source {
		if e := g.Set(r, Value{}, [4]Ref{targets[0], targets[0], targets[0], targets[0]}); e != nil {
			t.Fatal(e)
		}
	}
	audit(t, p)
	i := p.index[targets[0].page]
	if p.remote[i].count != maxRemoteSlots || len(p.index) != 1 {
		t.Fatal("duplicate reference count")
	}
	for _, r := range source {
		if e := g.Set(r, Value{}, [4]Ref{}); e != nil {
			t.Fatal(e)
		}
	}
	audit(t, p)
	if len(p.index) != 0 || len(p.free) != maxRemoteSlots {
		t.Fatal("remote roots not released")
	}
}

//go:noinline
func sparseFixture() (*Graph, Ref, weak.Pointer[page]) {
	g := New(1024)
	old, _ := g.Add(Value{}, [4]Ref{})
	g.Set(old, Value{}, [4]Ref{old})
	w := weak.Make(old.page)
	for range pageSize - 1 {
		g.Add(Value{}, [4]Ref{})
	}
	keep, _ := g.Add(Value{Payload: 77}, [4]Ref{})
	return g, keep, w
}

//go:noinline
func edgeFixture() (*Graph, Ref, weak.Pointer[page]) {
	g := New(1024)
	source, _ := g.Add(Value{}, [4]Ref{})
	for range pageSize - 1 {
		g.Add(Value{}, [4]Ref{})
	}
	target, _ := g.Add(Value{Payload: 99}, [4]Ref{})
	g.Set(source, Value{}, [4]Ref{target, target})
	for range pageSize {
		g.Add(Value{}, [4]Ref{})
	} // Current page no longer roots target.
	return g, source, weak.Make(target.page)
}
func requireCollected(t *testing.T, w weak.Pointer[page]) {
	t.Helper()
	for range 16 {
		runtime.GC()
		if w.Value() == nil {
			return
		}
	}
	t.Fatal("unreachable old page remained live in forced-GC fixture")
}
func TestPageGraphReachability(t *testing.T) {
	g, keep, w := sparseFixture()
	requireCollected(t, w)
	v, _, ok := keep.Read()
	if !ok || v.Payload != 77 {
		t.Fatal("current page lost")
	}
	runtime.KeepAlive(g)
	g, source, w := edgeFixture()
	runtime.GC()
	if w.Value() == nil {
		t.Fatal("live remote edge lost target")
	}
	_, edges, ok := source.Read()
	if !ok {
		t.Fatal("source lost")
	}
	v, _, ok = edges[0].Read()
	if !ok || v.Payload != 99 {
		t.Fatal("target payload lost")
	}
	edges = [4]Ref{}
	if e := g.Set(source, Value{}, [4]Ref{}); e != nil {
		t.Fatal(e)
	}
	requireCollected(t, w)
	runtime.KeepAlive(source)
	runtime.KeepAlive(g)
}

//go:noinline
func chainFixture(n int) Ref {
	g := New(uint32(n))
	var last Ref
	for i := range n {
		last, _ = g.Add(Value{Payload: uint64(i)}, [4]Ref{last})
	}
	return last
}
func TestEscapedRootAndConcurrentReads(t *testing.T) {
	root := chainFixture(4097)
	runtime.GC()
	check := func() bool {
		r := root
		for i := 4096; i >= 0; i-- {
			v, edges, ok := r.Read()
			if !ok || v.Payload != uint64(i) || r.ID() != uint32(i+1) {
				return false
			}
			r = edges[0]
		}
		return r.IsNil()
	}
	if !check() {
		t.Fatal("escaped root lost chain")
	}
	var wg sync.WaitGroup
	for range 8 {
		wg.Go(func() {
			for range 16 {
				if !check() {
					t.Error("concurrent read mismatch")
					return
				}
			}
		})
	}
	wg.Wait()
	runtime.KeepAlive(root)
}
func TestRecordLayout(t *testing.T) {
	if unsafe.Sizeof(record{}) != 32 || unsafe.Sizeof(Ref{}) != 16 {
		t.Fatal("unexpected amd64 layout")
	}
	typ := reflect.TypeFor[record]()
	for i := range typ.NumField() {
		f := typ.Field(i).Type
		if f.Kind() == reflect.Array {
			f = f.Elem()
		}
		if f.Kind() != reflect.Uint32 && f.Kind() != reflect.Uint64 {
			t.Fatal("pointer-bearing record field")
		}
	}
	t.Logf("record=%d page-header-and-records=%d remote=%d ref=%d graph=%d", unsafe.Sizeof(record{}), unsafe.Sizeof(page{}), unsafe.Sizeof(remote{}), unsafe.Sizeof(Ref{}), unsafe.Sizeof(Graph{}))
}

//go:noinline
func remoteCycleFixture() (*Graph, Ref, weak.Pointer[page], weak.Pointer[page]) {
	g := New(1024)
	a, _ := g.Add(Value{}, [4]Ref{})
	for range pageSize - 1 {
		g.Add(Value{}, [4]Ref{})
	}
	b, _ := g.Add(Value{}, [4]Ref{a})
	g.Set(a, Value{}, [4]Ref{b})
	wa, wb := weak.Make(a.page), weak.Make(b.page)
	for range pageSize - 1 {
		g.Add(Value{}, [4]Ref{})
	}
	keep, _ := g.Add(Value{Payload: 123}, [4]Ref{})
	return g, keep, wa, wb
}
func TestUnreachableRemoteCycleCollected(t *testing.T) {
	g, keep, a, b := remoteCycleFixture()
	requireCollected(t, a)
	requireCollected(t, b)
	v, _, ok := keep.Read()
	if !ok || v.Payload != 123 {
		t.Fatal("live page lost")
	}
	runtime.KeepAlive(g)
	runtime.KeepAlive(keep)
}
