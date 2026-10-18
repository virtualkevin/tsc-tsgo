package checker

// Simple mapper source/target pointers must be immutable after construction.
// Keep original leaves rooted as well as the composed identity mapping.
type foldedSimpleMapper struct {
	TypeMapperBase
	values map[*Type]*Type
	roots  []*TypeMapper
}

func (m *foldedSimpleMapper) Map(t *Type) *Type {
	if value, ok := m.values[t]; ok {
		return value
	}
	return t
}
func (p *mapperExecutionPlan) foldSimpleSpans() {
	// Branch targets are basic-block boundaries. Never fold across an entry.
	targets := make([]bool, len(p.code)+1)
	for _, ins := range p.code {
		if ins.op == mapperPlanComposite {
			targets[ins.jump] = true
		}
	}
	simple := func(i int) *SimpleTypeMapper {
		if i >= len(p.code) || p.code[i].op != mapperPlanLeaf {
			return nil
		}
		m, _ := p.code[i].mapper.data.(*SimpleTypeMapper)
		return m
	}
	for start := 0; start < len(p.code); {
		if simple(start) == nil {
			start++
			continue
		}
		end := start + 1
		for end < len(p.code) && !targets[end] && simple(end) != nil {
			end++
		}
		if end-start < 2 {
			start = end
			continue
		}
		f := &foldedSimpleMapper{values: make(map[*Type]*Type, end-start), roots: make([]*TypeMapper, 0, end-start)}
		f.data = f
		for i := start; i < end; i++ {
			f.roots = append(f.roots, p.code[i].mapper)
			source := simple(i).source
			if _, seen := f.values[source]; seen {
				continue
			}
			result := source
			for j := start; j < end; j++ {
				m := simple(j)
				if result == m.source {
					result = m.target
				}
			}
			f.values[source] = result
		}
		// Preserve offsets for all existing branches; unreachable old leaves remain
		// rooted and are skipped by this instruction, not executed again.
		p.code[start] = mapperPlanInstruction{op: mapperPlanFolded, mapper: &f.TypeMapper, jump: end}
		start = end
	}
}
