// Package graph is an isolated storage experiment, not a compiler implementation.
package graph

import "errors"

const pageBits = 8
const pageSize = 1 << pageBits
const pageMask = pageSize - 1

type handle uint32

// record deliberately contains no Go pointers. Reachability is provided by Graph.
type record struct {
	kind    uint32
	edges   [4]handle
	payload uint64
}
type page [pageSize]record

type Value struct {
	Kind    uint32
	Payload uint64
}

// Graph retains every allocated page for its lifetime. It has no reset/delete API.
// Mutation requires exclusive access. Concurrent reads require no concurrent writes.
type Graph struct {
	pages []*page
	count uint32
	limit uint32
}

// Ref carries its owner so a published reference keeps all its handle edges valid.
// The zero Ref is nil. IDs are meaningful only within this owner, not globally.
type Ref struct {
	owner *Graph
	id    handle
}

var ErrOwner = errors.New("reference belongs to another owner or is invalid")
var ErrFull = errors.New("graph handle capacity exhausted")

func New(limit uint32) *Graph           { return &Graph{limit: limit} }
func (g *Graph) Len() uint32            { return g.count }
func (g *Graph) AllocatedSlots() uint64 { return uint64(len(g.pages)) * pageSize }
func (r Ref) ID() uint32                { return uint32(r.id) }
func (r Ref) IsNil() bool               { return r.owner == nil && r.id == 0 }

func (g *Graph) valid(r Ref) bool {
	return r.owner == g && r.id != 0 && uint32(r.id) <= g.count
}
func (g *Graph) encode(edges [4]Ref) ([4]handle, error) {
	var out [4]handle
	for i, r := range edges {
		if r.IsNil() {
			continue
		}
		if !g.valid(r) {
			return [4]handle{}, ErrOwner
		}
		out[i] = r.id
	}
	return out, nil
}
func (g *Graph) slot(h handle) *record {
	// Internal callers have validated nonzero in-range IDs before decoding.
	index := uint32(h) - 1
	return &g.pages[index>>pageBits][index&pageMask]
}
func (g *Graph) Add(v Value, edges [4]Ref) (Ref, error) {
	encoded, err := g.encode(edges)
	if err != nil {
		return Ref{}, err
	}
	if g.count == g.limit {
		return Ref{}, ErrFull
	}
	if g.count&pageMask == 0 {
		g.pages = append(g.pages, new(page))
	}
	// count < limit <= MaxUint32, so this increment cannot wrap.
	g.count++
	h := handle(g.count)
	*g.slot(h) = record{kind: v.Kind, edges: encoded, payload: v.Payload}
	return Ref{g, h}, nil
}
func (g *Graph) Set(r Ref, v Value, edges [4]Ref) error {
	if !g.valid(r) {
		return ErrOwner
	}
	encoded, err := g.encode(edges)
	if err != nil {
		return err
	}
	*g.slot(r.id) = record{kind: v.Kind, edges: encoded, payload: v.Payload}
	return nil
}
func (r Ref) Read() (Value, [4]Ref, bool) {
	if r.owner == nil || !r.owner.valid(r) {
		return Value{}, [4]Ref{}, false
	}
	data := r.owner.slot(r.id)
	var edges [4]Ref
	for i, h := range data.edges {
		if h != 0 {
			edges[i] = Ref{r.owner, h}
		}
	}
	return Value{data.kind, data.payload}, edges, true
}
