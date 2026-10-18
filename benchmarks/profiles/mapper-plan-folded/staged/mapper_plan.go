package checker

// Experimental compiled control flow. Leaves retain their existing Map behavior;
// no result, inference, instantiation counter, or failure is memoized.
type mapperPlanOp uint8

const (
	mapperPlanLeaf mapperPlanOp = iota
	mapperPlanSave
	mapperPlanComposite
	mapperPlanFolded
)

type mapperPlanInstruction struct {
	op      mapperPlanOp
	mapper  *TypeMapper
	checker *Checker
	jump    int
}
type mapperExecutionPlan struct {
	code  []mapperPlanInstruction
	depth int
}

// The caller must own construction. Mapper graph topology must be immutable
// after publication. Leaf arrays/callbacks are not copied or evaluated here.
// Bounded expansion falls back without executing a single semantic operation.
func compileMapperExecutionPlan(root *TypeMapper) *mapperExecutionPlan {
	p := &mapperExecutionPlan{}
	active := map[*TypeMapper]bool{}
	visited := 0
	var emit func(*TypeMapper, int) bool
	emit = func(m *TypeMapper, depth int) bool {
		visited++
		if visited > 512 {
			return false
		}
		if m == nil || len(p.code) >= 256 || depth > 32 || active[m] {
			return false
		}
		active[m] = true
		defer delete(active, m)
		switch d := m.data.(type) {
		case *MergedTypeMapper:
			return emit(d.m1, depth) && emit(d.m2, depth)
		case *CompositeTypeMapper:
			p.code = append(p.code, mapperPlanInstruction{op: mapperPlanSave})
			if depth+1 > p.depth {
				p.depth = depth + 1
			}
			if !emit(d.m1, depth+1) || len(p.code) >= 256 {
				return false
			}
			branch := len(p.code)
			p.code = append(p.code, mapperPlanInstruction{op: mapperPlanComposite, mapper: d.m2, checker: d.c})
			if !emit(d.m2, depth) {
				return false
			}
			p.code[branch].jump = len(p.code)
			return true
		default:
			p.code = append(p.code, mapperPlanInstruction{op: mapperPlanLeaf, mapper: m})
			return true
		}
	}
	if !emit(root, 0) {
		return nil
	}
	p.foldSimpleSpans()
	return p
}

type mapperPlanInstantiate func(*Checker, *Type, *TypeMapper) *Type

func (p *mapperExecutionPlan) execute(t *Type, instantiate mapperPlanInstantiate) *Type {
	// Compile-time bound avoids per-query allocation and recursive interpreter calls.
	var saved [32]*Type
	sp := 0
	for pc := 0; pc < len(p.code); {
		ins := &p.code[pc]
		switch ins.op {
		case mapperPlanLeaf:
			t = ins.mapper.data.Map(t)
		case mapperPlanFolded:
			t = ins.mapper.data.Map(t)
			pc = ins.jump
			continue
		case mapperPlanSave:
			saved[sp] = t
			sp++
		case mapperPlanComposite:
			sp--
			original := saved[sp]
			saved[sp] = nil
			if t != original {
				t = instantiate(ins.checker, t, ins.mapper)
				pc = ins.jump
				continue
			}
		}
		pc++
	}
	return t
}
func (p *mapperExecutionPlan) Map(t *Type) *Type {
	return p.execute(t, func(c *Checker, t *Type, m *TypeMapper) *Type { return c.instantiateType(t, m) })
}
