// Package compact is an isolated representation experiment, not compiler code.
package compact

import "iter"

// Table copies alias the same mutable storage, like a Go map. The nil pointer
// is distinct from an allocated empty table. V will be *ast.Symbol at a future
// integration boundary; keeping this prototype generic permits isolated tests.
type Table[V any] = *storage[V]

type entry[V any] struct {
	key   string
	value V
}

type storage[V any] struct {
	large map[string]V
	used  uint8
	small [8]entry[V]
}

func New[V any](hint int) Table[V] {
	t := &storage[V]{}
	if hint > 8 {
		t.large = make(map[string]V, hint)
	}
	return t
}

func (t *storage[V]) Get(key string) (V, bool) {
	var zero V
	if t == nil {
		return zero, false
	}
	if t.large != nil {
		v, ok := t.large[key]
		return v, ok
	}
	for i := range t.small {
		if t.used&(1<<i) != 0 && t.small[i].key == key {
			return t.small[i].value, true
		}
	}
	return zero, false
}

func (t *storage[V]) Set(key string, value V) {
	if t == nil {
		panic("assignment to entry in nil table")
	}
	if t.large != nil {
		t.large[key] = value
		return
	}
	free := -1
	for i := range t.small {
		if t.used&(1<<i) == 0 {
			if free == -1 {
				free = i
			}
			continue
		}
		if t.small[i].key == key {
			t.small[i].value = value
			return
		}
	}
	if free >= 0 {
		t.small[free] = entry[V]{key, value}
		t.used |= 1 << free
		return
	}
	// Promotion changes the shared state, so existing table aliases observe it.
	t.large = make(map[string]V, 9)
	for _, e := range t.small {
		t.large[e.key] = e.value
	}
	clear(t.small[:])
	t.used = 0
	t.large[key] = value
}

func (t *storage[V]) Len() int {
	if t == nil {
		return 0
	}
	if t.large != nil {
		return len(t.large)
	}
	n := 0
	for bits := t.used; bits != 0; bits &= bits - 1 {
		n++
	}
	return n
}

func (t *storage[V]) Delete(key string) {
	if t == nil {
		return
	}
	if t.large != nil {
		delete(t.large, key)
		return
	}
	for i := range t.small {
		if t.used&(1<<i) != 0 && t.small[i].key == key {
			t.small[i] = entry[V]{}
			t.used &^= 1 << i
			return
		}
	}
}

func (t *storage[V]) Clear() {
	if t == nil {
		return
	}
	if t.large != nil {
		clear(t.large)
		return
	}
	clear(t.small[:])
	t.used = 0
}

// All reads current values at iteration time. A small iteration snapshots only
// the original keys: deletion suppresses an entry, replacement exposes the new
// value, and insertion may be omitted, as Go map iteration permits. Promotion
// during a callback is safe because Get reads the same shared table state.
// Enumeration alone does not force materialization of a Go map.
func (t *storage[V]) All() iter.Seq2[string, V] {
	return func(yield func(string, V) bool) {
		if t == nil {
			return
		}
		if t.large != nil {
			for k, v := range t.large {
				if !yield(k, v) {
					return
				}
			}
			return
		}
		var keys [8]string
		n := 0
		for i, e := range t.small {
			if t.used&(1<<i) != 0 {
				keys[n] = e.key
				n++
			}
		}
		for _, k := range keys[:n] {
			if v, ok := t.Get(k); ok && !yield(k, v) {
				return
			}
		}
	}
}

func (t *storage[V]) Values() iter.Seq[V] {
	return func(yield func(V) bool) {
		for _, v := range t.All() {
			if !yield(v) {
				return
			}
		}
	}
}

func (t *storage[V]) Clone() Table[V] {
	if t == nil {
		return nil
	}
	r := New[V](t.Len())
	for k, v := range t.All() {
		r.Set(k, v)
	}
	return r
}
