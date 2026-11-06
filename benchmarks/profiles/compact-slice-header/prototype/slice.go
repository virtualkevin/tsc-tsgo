package compactslice

import "unsafe"

// Slice stores a slice header, not a copy of its elements. Copies share the
// underlying array just as ordinary slices do. Concurrent mutation of the
// header or array requires the same synchronization as ordinary slices.
// Only From creates nonzero values; fields must not be independently mutated.
type Slice[T any] struct {
	data  unsafe.Pointer
	shape uint64
}

const indirectShape = ^uint64(0)

func pack(length, capacity uint64) (uint64, bool) {
	if length > capacity || capacity > uint64(^uint32(0)) {
		return 0, false
	}
	shape := capacity<<32 | length
	return shape, shape != indirectShape
}

func From[T any](s []T) Slice[T] {
	if shape, ok := pack(uint64(len(s)), uint64(cap(s))); ok {
		return Slice[T]{data: unsafe.Pointer(unsafe.SliceData(s)), shape: shape}
	}
	return indirect(s)
}

//go:noinline
func indirect[T any](s []T) Slice[T] {
	// The escaping header is immutable. It keeps the exact ordinary slice
	// representation, including very large zero-sized-element slices.
	return Slice[T]{data: unsafe.Pointer(&s), shape: indirectShape}
}

func (s Slice[T]) Values() []T {
	if s.shape == indirectShape {
		return *(*[]T)(s.data)
	}
	return unsafe.Slice((*T)(s.data), int(s.shape>>32))[:int(uint32(s.shape))]
}
