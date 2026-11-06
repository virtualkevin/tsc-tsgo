package checker

import "unsafe"

// Slice stores a slice header, not a copy of its elements. Copies share the
// underlying array just as ordinary slices do. Concurrent mutation of the
// header or array requires the same synchronization as ordinary slices.
// Only compactSliceFrom creates nonzero values; fields must not be independently mutated.
type compactSlice[T any] struct {
	data  unsafe.Pointer
	shape uint64
}

const compactSliceIndirectShape = ^uint64(0)

func packCompactSlice(length, capacity uint64) (uint64, bool) {
	if length > capacity || capacity > uint64(^uint32(0)) {
		return 0, false
	}
	shape := capacity<<32 | length
	return shape, shape != compactSliceIndirectShape
}

func compactSliceFrom[T any](s []T) compactSlice[T] {
	if shape, ok := packCompactSlice(uint64(len(s)), uint64(cap(s))); ok {
		return compactSlice[T]{data: unsafe.Pointer(unsafe.SliceData(s)), shape: shape}
	}
	return indirectCompactSlice(s)
}

//go:noinline
func indirectCompactSlice[T any](s []T) compactSlice[T] {
	// The escaping header is immutable. It keeps the exact ordinary slice
	// representation, including very large zero-sized-element slices.
	return compactSlice[T]{data: unsafe.Pointer(&s), shape: compactSliceIndirectShape}
}

func (s compactSlice[T]) Values() []T {
	if s.shape == compactSliceIndirectShape {
		return *(*[]T)(s.data)
	}
	return unsafe.Slice((*T)(s.data), int(s.shape>>32))[:int(uint32(s.shape))]
}
