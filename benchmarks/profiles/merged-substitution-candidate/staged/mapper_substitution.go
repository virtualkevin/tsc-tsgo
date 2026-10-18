package checker

// Immutable simple-only trees retain their original topology for mapper Kind,
// structural ordering, and GC lifetime. All publication occurs in construction.
func simpleMapperWeight(m *TypeMapper) uint16 {
	if m == nil {
		return 0
	}
	switch d := m.data.(type) {
	case *SimpleTypeMapper:
		return 1
	case *MergedTypeMapper:
		return d.simpleWeight
	default:
		return 0
	}
}
func (m *MergedTypeMapper) initializeSubstitution() {
	a, b := simpleMapperWeight(m.m1), simpleMapperWeight(m.m2)
	if a == 0 || b == 0 {
		return
	}
	count := a + b
	if count > 256 {
		count = 257
	}
	m.simpleWeight = count
	// Fixed policy: materialize only at geometric tree sizes, not every ancestor.
	// Small trees keep the original evaluator; no adaptive mutable query counters.
	if count < 16 || count > 256 || count&(count-1) != 0 {
		return
	}
	leaves := make([]*SimpleTypeMapper, 0, int(count))
	var visit func(*TypeMapper)
	visit = func(node *TypeMapper) {
		switch d := node.data.(type) {
		case *SimpleTypeMapper:
			leaves = append(leaves, d)
		case *MergedTypeMapper:
			visit(d.m1)
			visit(d.m2)
		}
	}
	visit(m.m1)
	visit(m.m2)
	values := make(map[*Type]*Type, len(leaves))
	for _, leaf := range leaves {
		source := leaf.source
		if _, seen := values[source]; seen {
			continue
		}
		result := source
		for _, next := range leaves {
			if result == next.source {
				result = next.target
			}
		}
		values[source] = result
	}
	m.substitution = values
}
