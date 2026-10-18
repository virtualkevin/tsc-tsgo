package checker

import (
	"os"
	"runtime"
	"slices"
	"weak"
)

const typeLivenessStride uint64 = 64
const typeLivenessLimit = 65536

type typeLivenessSample struct {
	ref   weak.Pointer[Type]
	id    TypeId
	flags TypeFlags
}

type typeLivenessCensus struct {
	created  uint64
	overflow uint64
	samples  []typeLivenessSample
}

func newTypeLivenessCensus() *typeLivenessCensus {
	if os.Getenv("TSC_GO_TYPE_LIVENESS_CENSUS") == "" {
		return nil
	}
	return &typeLivenessCensus{}
}

func (l *typeLivenessCensus) observe(t *Type) {
	l.created++
	if (l.created-1)%typeLivenessStride != 0 {
		return
	}
	if len(l.samples) == typeLivenessLimit {
		l.overflow++
		return
	}
	l.samples = append(l.samples, typeLivenessSample{weak.Make(t), t.id, t.flags})
}

type TypeLivenessKind struct {
	CreationFlags TypeFlags
	Sampled       uint64
	Available     uint64
	Cleared       uint64
}

type TypeLivenessSnapshot struct {
	CheckerID          uint32
	Created            uint64
	SemanticTypeCount  uint32
	Stride             uint64
	Limit              int
	Eligible           uint64
	Sampled            uint64
	Overflow           uint64
	Available          uint64
	Cleared            uint64
	IdentityMismatches uint64
	Kinds              []TypeLivenessKind
}

// Read under exclusive checker ownership, after the caller's diagnostic GC.
// Available weak values are not proof that a type is semantically necessary.
func (c *Checker) TypeLivenessSnapshot() (TypeLivenessSnapshot, bool) {
	l := c.typeLivenessCensus
	if l == nil {
		return TypeLivenessSnapshot{}, false
	}
	r := TypeLivenessSnapshot{CheckerID: c.id, Created: l.created, SemanticTypeCount: c.TypeCount, Stride: typeLivenessStride, Limit: typeLivenessLimit, Sampled: uint64(len(l.samples)), Overflow: l.overflow}
	if l.created != 0 {
		r.Eligible = (l.created-1)/typeLivenessStride + 1
	}
	kinds := map[TypeFlags]*TypeLivenessKind{}
	for _, s := range l.samples {
		k := kinds[s.flags]
		if k == nil {
			k = &TypeLivenessKind{CreationFlags: s.flags}
			kinds[s.flags] = k
		}
		k.Sampled++
		if t := s.ref.Value(); t == nil {
			r.Cleared++
			k.Cleared++
		} else {
			r.Available++
			k.Available++
			if t.id != s.id || t.checker != c {
				r.IdentityMismatches++
			}
		}
	}
	for _, k := range kinds {
		r.Kinds = append(r.Kinds, *k)
	}
	slices.SortFunc(r.Kinds, func(a, b TypeLivenessKind) int {
		if a.CreationFlags < b.CreationFlags {
			return -1
		}
		if a.CreationFlags > b.CreationFlags {
			return 1
		}
		return 0
	})
	runtime.KeepAlive(c)
	return r, true
}
