// Package graph is a standalone ownership experiment, not a compiler port.
package graph

import "errors"

const pageSize = 256
const slotBits = 9 // Low values 1..256 identify slots; zero means nil.
const slotMask = (1 << slotBits) - 1
const maxRemoteSlots = pageSize * 4

type handle uint32
type owner struct{ nonzero byte }
type record struct {
	id      uint32
	kind    uint32
	edges   [4]handle
	payload uint64
}
type remote struct {
	target *page
	count  uint16
}

// Only live outgoing page edges are strong roots. Metadata never points to Graph.
type page struct {
	records [pageSize]record
	owner   *owner
	used    uint16
	remote  []remote
	index   map[*page]uint16
	free    []uint16
}

type Value struct {
	Kind    uint32
	Payload uint64
}

// Graph roots only the current allocation page. It must not be copied and then
// independently mutated. Mutation requires exclusive ownership; completed reads
// can be concurrent. There is no record deletion, relocation or identity reuse.
type Graph struct {
	current        *page
	owner          *owner
	count          uint32
	limit          uint32
	pagesAllocated uint32
}

// Ref roots one page and its outgoing page graph. Its zero value represents nil.
// Page/slot identity is stable even after the allocating Graph is discarded.
type Ref struct {
	page *page
	slot uint16
}

var ErrOwner = errors.New("invalid or foreign reference")
var ErrFull = errors.New("graph identity capacity exhausted")

func New(limit uint32) *Graph { return &Graph{owner: new(owner), limit: limit} }
func (g *Graph) Len() uint32  { return g.count }

// AllocatedSlots counts cumulative allocation, not currently live storage.
func (g *Graph) AllocatedSlots() uint64 { return uint64(g.pagesAllocated) * pageSize }
func (r Ref) IsNil() bool               { return r.page == nil && r.slot == 0 }
func (r Ref) valid() bool               { return r.page != nil && r.page.owner != nil && r.slot < r.page.used }
func (r Ref) ID() uint32 {
	if !r.valid() {
		return 0
	}
	return r.page.records[r.slot].id
}
func (g *Graph) valid(r Ref) bool { return r.valid() && r.page.owner == g.owner }
func (g *Graph) validate(edges [4]Ref) error {
	for _, r := range edges {
		if !r.IsNil() && !g.valid(r) {
			return ErrOwner
		}
	}
	return nil
}
func (p *page) encode(edges [4]Ref) (out [4]handle) {
	for i, r := range edges {
		if r.IsNil() {
			continue
		}
		h := uint32(r.slot) + 1
		if r.page != p {
			index, exists := p.index[r.page]
			if !exists {
				if len(p.free) > 0 {
					index = p.free[len(p.free)-1]
					p.free = p.free[:len(p.free)-1]
				} else {
					if len(p.remote) >= maxRemoteSlots {
						panic("live edge cardinality invariant")
					}
					index = uint16(len(p.remote))
					p.remote = append(p.remote, remote{})
				}
				if p.index == nil {
					p.index = make(map[*page]uint16)
				}
				p.index[r.page] = index
				p.remote[index].target = r.page
			}
			p.remote[index].count++ // At most 4*256 live edges per page.
			h |= (uint32(index) + 1) << slotBits
		}
		out[i] = handle(h)
	}
	return
}
func (p *page) unlink(edges [4]handle) {
	for _, h := range edges {
		ordinal := uint32(h) >> slotBits
		if ordinal == 0 {
			continue
		}
		index := uint16(ordinal - 1)
		entry := &p.remote[index]
		entry.count--
		if entry.count == 0 {
			delete(p.index, entry.target)
			entry.target = nil
			p.free = append(p.free, index)
		}
	}
}
func (g *Graph) Add(v Value, edges [4]Ref) (Ref, error) {
	if err := g.validate(edges); err != nil {
		return Ref{}, err
	}
	if g.count == g.limit {
		return Ref{}, ErrFull
	}
	if g.current == nil || g.current.used == pageSize {
		g.current = &page{owner: g.owner}
		g.pagesAllocated++
	}
	p := g.current
	slot := p.used
	encoded := p.encode(edges)
	g.count++
	p.records[slot] = record{id: g.count, kind: v.Kind, edges: encoded, payload: v.Payload}
	p.used++
	return Ref{p, slot}, nil
}
func (g *Graph) Set(r Ref, v Value, edges [4]Ref) error {
	if !g.valid(r) {
		return ErrOwner
	}
	if err := g.validate(edges); err != nil {
		return err
	}
	// Inputs are validated and strongly rooted before removing old edges. No user
	// callback or supported concurrent reader can see this intermediate state.
	p := r.page
	old := p.records[r.slot]
	p.unlink(old.edges)
	encoded := p.encode(edges)
	p.records[r.slot] = record{id: old.id, kind: v.Kind, edges: encoded, payload: v.Payload}
	return nil
}
func (r Ref) Read() (Value, [4]Ref, bool) {
	if !r.valid() {
		return Value{}, [4]Ref{}, false
	}
	data := r.page.records[r.slot]
	var edges [4]Ref
	for i, h := range data.edges {
		if h == 0 {
			continue
		}
		p := r.page
		ordinal := uint32(h) >> slotBits
		if ordinal != 0 {
			p = p.remote[ordinal-1].target
		}
		edges[i] = Ref{p, uint16((uint32(h) & slotMask) - 1)}
	}
	return Value{data.kind, data.payload}, edges, true
}
