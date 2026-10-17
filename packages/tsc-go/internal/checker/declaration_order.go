package checker

import (
	"slices"

	"github.com/microsoft/typescript-go/internal/ast"
)

// This state belongs to one comparison, never to the process or checker. Normal
// type checking retains its ID-based total order; declaration serialization can
// detect those ties and order them independently of parallel checker history.
type declarationTypeOrder struct {
	structuralTies bool
	usedIDs        bool
}

func compareOtherTypeMappers(m1, m2 *TypeMapper, order *declarationTypeOrder) int {
	if rank := otherMapperRank(m1) - otherMapperRank(m2); rank != 0 {
		return rank
	}
	switch a := m1.data.(type) {
	case *CompositeTypeMapper:
		b := m2.data.(*CompositeTypeMapper)
		if r := compareTypeMappersWithOrder(a.m1, b.m1, order); r != 0 {
			return r
		}
		return compareTypeMappersWithOrder(a.m2, b.m2, order)
	case *ArrayToSingleTypeMapper:
		b := m2.data.(*ArrayToSingleTypeMapper)
		if r := compareTypeListsWithOrder(a.sources, b.sources, order); r != 0 {
			return r
		}
		return compareTypesWithOrder(a.target, b.target, order)
	}
	return 0
}

func otherMapperRank(m *TypeMapper) int {
	switch m.data.(type) {
	case *CompositeTypeMapper:
		return 1
	case *ArrayToSingleTypeMapper:
		return 2
	default:
		return 3
	}
}

// Visit the declarations reached by a type's identity breadth first. Source
// declarations precede library declarations, matching the original TS port.
// Bounds prevent recursive or highly connected types from growing the walk.
func (c *Checker) declarationPlaces(t *Type) []int64 {
	var places, libraryPlaces []int64
	queue := []*Type{t}
	seen := make(map[*Type]bool)
	visit := func(symbol *ast.Symbol) {
		if symbol == nil || len(symbol.Declarations) == 0 {
			return
		}
		node := symbol.Declarations[0]
		file := ast.GetSourceFileOfNode(node)
		place := int64(c.fileIndexMap[file])*0x4000000 + int64(node.Pos())
		if file.IsDeclarationFile {
			libraryPlaces = append(libraryPlaces, place)
		} else {
			places = append(places, place)
		}
	}
	var mapper func(*TypeMapper)
	mapper = func(m *TypeMapper) {
		if m == nil {
			return
		}
		switch m := m.data.(type) {
		case *SimpleTypeMapper:
			queue = append(queue, m.target)
		case *ArrayTypeMapper:
			queue = append(queue, m.targets...)
		case *ArrayToSingleTypeMapper:
			queue = append(queue, m.target)
		case *MergedTypeMapper:
			mapper(m.m1)
			mapper(m.m2)
		case *CompositeTypeMapper:
			mapper(m.m1)
			mapper(m.m2)
		}
	}
	for k := 0; k < len(queue) && len(places) < 16 && k < 64; k++ {
		u := queue[k]
		if seen[u] {
			continue
		}
		seen[u] = true
		visit(u.symbol)
		if u.alias != nil {
			visit(u.alias.symbol)
			queue = append(queue, u.alias.typeArguments...)
		}
		if u.flags&TypeFlagsUnionOrIntersection != 0 {
			queue = append(queue, u.Types()...)
		}
		if u.flags&TypeFlagsObject != 0 {
			if u.objectFlags&ObjectFlagsReference != 0 && u.AsTypeReference().node == nil {
				queue = append(queue, u.AsTypeReference().resolvedTypeArguments...)
			}
			mapper(u.AsObjectType().mapper)
		}
	}
	return append(places, libraryPlaces...)
}

// Only reorder adjacent constituents whose normal comparison falls back to IDs
// (including nested comparisons). Keep the checker's canonical union untouched.
func (c *Checker) inDeclarationOrder(types []*Type) []*Type {
	var result []*Type
	start := 0
	for i := 1; i <= len(types); i++ {
		order := declarationTypeOrder{}
		if i < len(types) {
			compareTypesWithOrder(types[i-1], types[i], &order)
			if order.usedIDs {
				continue
			}
		}
		if i-start > 1 {
			run := types[start:i]
			indices := make([]int, len(run))
			places := make([][]int64, len(run))
			for k, t := range run {
				indices[k] = k
				places[k] = c.declarationPlaces(t)
			}
			order.structuralTies = true
			slices.SortFunc(indices, func(a, b int) int {
				if r := slices.Compare(places[a], places[b]); r != 0 {
					return r
				}
				if r := compareTypesWithOrder(run[a], run[b], &order); r != 0 {
					return r
				}
				return a - b
			})
			for k, index := range indices {
				if index != k {
					if result == nil {
						result = slices.Clone(types)
					}
					result[start+k] = run[index]
				}
			}
		}
		start = i
	}
	if result != nil {
		return result
	}
	return types
}
