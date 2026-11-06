package graph

import (
	"encoding/json"
	"fmt"
	"os"
	"reflect"
	"runtime"
	"strconv"
	"testing"
)

// Stable typed pointer pages, retaining only the current page in the allocator.
// The input domain is one graph with valid prior-node edges, matching the compact
// constructors. Pointer records need no extra decoder/owner for edge reachability.
type pointerRecord struct {
	id      uint32
	kind    uint32
	edges   [4]*pointerRecord
	payload uint64
}
type pointerPage [pageSize]pointerRecord
type pointerBuilder struct {
	current *pointerPage
	count   uint32
}

func (g *pointerBuilder) add(v Value, edges [4]*pointerRecord) *pointerRecord {
	if g.count&(pageSize-1) == 0 {
		g.current = new(pointerPage)
	}
	r := &g.current[g.count&(pageSize-1)]
	g.count++
	*r = pointerRecord{id: g.count, kind: v.Kind, edges: edges, payload: v.Payload}
	return r
}

func fixtureValue(id uint32) Value { return Value{id % 23, uint64(id) * 0x100000001} }
func fixtureEdges(index uint32, shape string) [4]uint32 {
	if index == 0 || shape == "sparse" {
		return [4]uint32{}
	}
	if shape == "local" {
		first := (index/pageSize)*pageSize + 1
		if first > index {
			return [4]uint32{index, index, index, index}
		}
		return [4]uint32{index, first, first + (index-first)/2, index}
	}
	if shape != "linked" {
		panic("bad shape")
	}
	return [4]uint32{index, uint32((uint64(index)*0x9e3779b97f4a7c15>>32)%uint64(index)) + 1, index/2 + 1, uint32(((uint64(index)*1103515245+12345)>>8)%uint64(index)) + 1}
}

// Both constructors use an externally usable reference table while constructing.
// It is temporary; noinline ensures it has left the stack before retention probes.
//
//go:noinline
func buildCompact(n uint32, shape string) Ref {
	g := New(n)
	refs := make([]Ref, n+1)
	for i := uint32(0); i < n; i++ {
		ids := fixtureEdges(i, shape)
		var edges [4]Ref
		for j, id := range ids {
			edges[j] = refs[id]
		}
		r, err := g.Add(fixtureValue(i+1), edges)
		if err != nil {
			panic(err)
		}
		refs[i+1] = r
	}
	return refs[n]
}

//go:noinline
func buildPointer(n uint32, shape string) *pointerRecord {
	var g pointerBuilder
	refs := make([]*pointerRecord, n+1)
	for i := uint32(0); i < n; i++ {
		ids := fixtureEdges(i, shape)
		var edges [4]*pointerRecord
		for j, id := range ids {
			edges[j] = refs[id]
		}
		refs[i+1] = g.add(fixtureValue(i+1), edges)
	}
	return refs[n]
}
func decodeEdge(source *page, h handle) Ref {
	if h == 0 {
		return Ref{}
	}
	target := source
	if ordinal := uint32(h) >> slotBits; ordinal != 0 {
		target = source.remote[ordinal-1].target
	}
	return Ref{target, uint16((uint32(h) & slotMask) - 1)}
}
func compactWalk(root Ref) uint64 {
	var sum uint64
	for r := root; !r.IsNil(); {
		data := &r.page.records[r.slot]
		sum += uint64(data.kind) + data.payload
		for _, h := range data.edges {
			if h != 0 {
				edge := decodeEdge(r.page, h)
				sum += edge.page.records[edge.slot].payload
			}
		}
		r = decodeEdge(r.page, data.edges[0])
	}
	return sum
}
func pointerWalk(root *pointerRecord) uint64 {
	var sum uint64
	for r := root; r != nil; r = r.edges[0] {
		sum += uint64(r.kind) + r.payload
		for _, edge := range r.edges {
			if edge != nil {
				sum += edge.payload
			}
		}
	}
	return sum
}
func pointerRead(r *pointerRecord) (Value, [4]*pointerRecord, bool) {
	if r == nil {
		return Value{}, [4]*pointerRecord{}, false
	}
	return Value{r.kind, r.payload}, r.edges, true
}
func compactPublicWalk(root Ref) uint64 {
	var sum uint64
	for r := root; !r.IsNil(); {
		v, edges, ok := r.Read()
		if !ok {
			panic("bad compact root")
		}
		sum += uint64(v.Kind) + v.Payload
		for _, edge := range edges {
			if !edge.IsNil() {
				v, _, ok := edge.Read()
				if !ok {
					panic("bad compact edge")
				}
				sum += v.Payload
			}
		}
		r = edges[0]
	}
	return sum
}
func pointerPublicWalk(root *pointerRecord) uint64 {
	var sum uint64
	for r := root; r != nil; {
		v, edges, ok := pointerRead(r)
		if !ok {
			panic("bad pointer root")
		}
		sum += uint64(v.Kind) + v.Payload
		for _, edge := range edges {
			if edge != nil {
				v, _, ok := pointerRead(edge)
				if !ok {
					panic("bad pointer edge")
				}
				sum += v.Payload
			}
		}
		r = edges[0]
	}
	return sum
}
func fixtureChecksum(n uint32, shape string) uint64 {
	var sum uint64
	for id := uint32(1); id <= n; id++ {
		v := fixtureValue(id)
		sum += uint64(v.Kind) + v.Payload
		for _, edge := range fixtureEdges(id-1, shape) {
			if edge != 0 {
				sum += fixtureValue(edge).Payload
			}
		}
	}
	return sum
}

func TestStorageFixtureEquality(t *testing.T) {
	for _, shape := range []string{"linked", "local", "sparse"} {
		for _, n := range []uint32{1, 255, 256, 257, 4096, 262144} {
			cr, pr := buildCompact(n, shape), buildPointer(n, shape)
			if shape != "sparse" {
				want := fixtureChecksum(n, shape)
				if compactWalk(cr) != want || pointerWalk(pr) != want || compactPublicWalk(cr) != want || pointerPublicWalk(pr) != want {
					t.Fatal("traversal mismatch", shape, n)
				}
			}
			for id := n; id != 0; id-- {
				v, ce, ok := cr.Read()
				pv, pe, pok := pointerRead(pr)
				if !ok || !pok || v != fixtureValue(id) || pv != v || cr.ID() != id || pr.id != id {
					t.Fatal("record mismatch", shape, n, id)
				}
				expected := fixtureEdges(id-1, shape)
				for j, e := range ce {
					if e.ID() != expected[j] {
						t.Fatal("compact edge mismatch", shape, id, j)
					}
					if expected[j] == 0 {
						if pe[j] != nil {
							t.Fatal("pointer nil mismatch")
						}
					} else if pe[j] == nil || pe[j].id != expected[j] || pe[j].payload != fixtureValue(expected[j]).Payload {
						t.Fatal("pointer edge mismatch")
					}
				}
				if shape == "sparse" {
					break
				}
				cr, pr = ce[0], pe[0]
			}
		}
	}
	t.Logf("pointerRecord=%d compactRecord=%d pointerPage=%d compactPage=%d", reflect.TypeOf(pointerRecord{}).Size(), reflect.TypeOf(record{}).Size(), reflect.TypeOf(pointerPage{}).Size(), reflect.TypeOf(page{}).Size())
}
func TestStoragePointerPageLifetime(t *testing.T) {
	root := buildPointer(8193, "linked")
	for range 3 {
		runtime.GC()
	}
	if pointerWalk(root) != fixtureChecksum(8193, "linked") {
		t.Fatal("stable pointer pages lost")
	}
	runtime.KeepAlive(root)
}

var compactSink Ref
var pointerSink *pointerRecord
var checksumSink uint64

func BenchmarkStorage(b *testing.B) {
	for _, shape := range []string{"linked", "local"} {
		b.Run(shape, func(b *testing.B) {
			for _, op := range []string{"construct", "internal", "public"} {
				b.Run(op, func(b *testing.B) {
					for _, side := range []string{"pointer", "compact"} {
						b.Run(side, func(b *testing.B) {
							for _, n := range []uint32{4096, 262144} {
								b.Run(fmt.Sprintf("n%d", n), func(b *testing.B) {
									var cr Ref
									var pr *pointerRecord
									if op != "construct" {
										if side == "compact" {
											cr = buildCompact(n, shape)
										} else {
											pr = buildPointer(n, shape)
										}
									}
									b.ReportAllocs()
									b.ResetTimer()
									for b.Loop() {
										switch op {
										case "construct":
											if side == "compact" {
												compactSink = buildCompact(n, shape)
											} else {
												pointerSink = buildPointer(n, shape)
											}
										case "internal":
											if side == "compact" {
												checksumSink = compactWalk(cr)
											} else {
												checksumSink = pointerWalk(pr)
											}
										case "public":
											if side == "compact" {
												checksumSink = compactPublicWalk(cr)
											} else {
												checksumSink = pointerPublicWalk(pr)
											}
										}
									}
									runtime.KeepAlive(cr)
									runtime.KeepAlive(pr)
								})
							}
						})
					}
				})
			}
		})
	}
}
func compactMetadata(root Ref) map[string]uint64 {
	out := map[string]uint64{}
	seen := map[*page]bool{}
	stack := []*page{root.page}
	for len(stack) > 0 {
		p := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if p == nil || seen[p] {
			continue
		}
		seen[p] = true
		out["pages"]++
		out["remoteLength"] += uint64(len(p.remote))
		out["remoteCapacity"] += uint64(cap(p.remote))
		out["remoteIndexEntries"] += uint64(len(p.index))
		out["freeLength"] += uint64(len(p.free))
		out["freeCapacity"] += uint64(cap(p.free))
		for _, r := range p.remote {
			if r.target != nil {
				stack = append(stack, r.target)
			}
		}
	}
	return out
}

// Separate fresh-process endpoint measurement. Timings here are not benchmarks.
func TestStorageRetentionProbe(t *testing.T) {
	side := os.Getenv("GRAPH_PROBE_SIDE")
	if side == "" {
		t.Skip("explicit retention probe only")
	}
	n64, err := strconv.ParseUint(os.Getenv("GRAPH_PROBE_N"), 10, 32)
	if err != nil || (n64 != 4096 && n64 != 262144) {
		t.Fatal("bad size")
	}
	shape := os.Getenv("GRAPH_PROBE_SHAPE")
	if shape != "linked" && shape != "local" && shape != "sparse" {
		t.Fatal("bad shape")
	}
	n := uint32(n64)
	var before, after runtime.MemStats
	runtime.GC()
	runtime.GC()
	runtime.ReadMemStats(&before)
	var cr Ref
	var pr *pointerRecord
	switch side {
	case "compact":
		cr = buildCompact(n, shape)
	case "pointer":
		pr = buildPointer(n, shape)
	default:
		t.Fatal("bad side")
	}
	runtime.GC()
	runtime.GC()
	runtime.ReadMemStats(&after)
	var v Value
	if side == "compact" {
		v, _, _ = cr.Read()
	} else {
		v, _, _ = pointerRead(pr)
	}
	if v != fixtureValue(n) {
		t.Fatal("root lost")
	}
	report := map[string]any{"side": side, "shape": shape, "records": n, "before": before, "after": after, "heapAllocDelta": int64(after.HeapAlloc) - int64(before.HeapAlloc), "heapObjectsDelta": int64(after.HeapObjects) - int64(before.HeapObjects), "totalAllocDelta": after.TotalAlloc - before.TotalAlloc, "rootPayload": v.Payload, "compactMetadata": map[string]uint64(nil)}
	if side == "compact" {
		report["compactMetadata"] = compactMetadata(cr) // After endpoint snapshot; metadata traversal allocations are excluded.
	}
	data, err := json.Marshal(report)
	if err != nil {
		t.Fatal(err)
	}
	t.Log("RETENTION " + string(data))
	runtime.KeepAlive(cr)
	runtime.KeepAlive(pr)
}
