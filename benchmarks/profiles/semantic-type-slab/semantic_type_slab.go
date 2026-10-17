package checker

// semanticTypeSlab batches typed allocations without moving published objects.
// Only the current slab is rooted here; older slabs remain alive through their
// escaped objects. There is no reset or reuse of published storage. One escaped
// object can retain up to 31 neighbors and their graphs, so pages stay small.
// Like the checker itself, allocation requires exclusive ownership.
type semanticTypeSlab[T any] struct {
	current []T
}

func (s *semanticTypeSlab[T]) New() *T {
	if len(s.current) == cap(s.current) {
		s.current = make([]T, 0, 32)
	}
	index := len(s.current)
	s.current = s.current[:index+1]
	return &s.current[index]
}
