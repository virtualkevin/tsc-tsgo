package scratch

import "slices"

// Generic prototype only: no compiler implementation or cache of semantic facts.
type Groups[T comparable] struct {
	byName  map[string][]T
	names   []string
	buffers [][]T
}

type Pool[T comparable] struct{ idle *Groups[T] }

func (p *Pool[T]) Acquire() *Groups[T] {
	g := p.idle
	p.idle = nil // A recursive operation cannot borrow an active frame.
	if g == nil {
		g = &Groups[T]{byName: make(map[string][]T)}
	}
	return g
}

func (g *Groups[T]) Add(name string, value T) {
	values, seen := g.byName[name]
	if !seen {
		i := len(g.names)
		g.names = append(g.names, name)
		if i == len(g.buffers) {
			g.buffers = append(g.buffers, nil)
		}
		values = g.buffers[i][:0]
	}
	if !slices.Contains(values, value) {
		values = append(values, value)
		g.byName[name] = values
	}
}

// Values and Names are borrows valid only until Release. Add during consumption
// is forbidden, matching construction-then-consumption in the target algorithm.
func (g *Groups[T]) Names() []string        { return g.names }
func (g *Groups[T]) Values(name string) []T { return g.byName[name] }

func (p *Pool[T]) Release(g *Groups[T]) {
	// Bound idle retention; unusually wide frames are left to the GC.
	keep := len(g.names) <= 1024
	for i, name := range g.names {
		values := g.byName[name]
		clear(values[:cap(values)])
		if cap(values) <= 64 {
			g.buffers[i] = values[:0]
		} else {
			g.buffers[i] = nil
		}
	}
	clear(g.byName)
	clear(g.names)
	g.names = g.names[:0]
	if keep && p.idle == nil {
		p.idle = g
	}
}
