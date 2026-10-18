package checker

import (
	"slices"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/core"
)

// Freeze an entry order once: unlike JavaScript Map, Go map iteration cannot be
// used independently to construct positions and then interpret packed states.
type instantiatedMemberSource struct {
	entries         []*ast.Symbol
	positions       map[string]int
	lastMemberNames *memberNames
}

// A name layout is shared by instantiations of one source with the same
// property order. Go maps have no stable iteration order to preserve separately.
type memberNames struct {
	names     []string
	positions map[string]int
}

type instantiatedMemberListKey struct {
	first  **ast.Symbol
	length int
}

type inheritedPendingMembers struct {
	typ        *StructuredType
	properties []*ast.Symbol
}

const (
	pendingMemberSkipped      uint32 = 0
	pendingMemberInstantiated uint32 = 1
	pendingMemberKept         uint32 = 3
)

// Only symbol allocation is deferred. The decision to reuse the original symbol
// is captured before signatures, indexes and bases can resolve more symbol types.
type pendingInstantiatedMembers struct {
	memberNames            *memberNames
	materializedProperties []*ast.Symbol
	checker                *Checker
	source                 *instantiatedMemberSource
	mapper                 *TypeMapper
	states                 []uint32
	instantiated           ast.SymbolTable
	bases                  []inheritedPendingMembers
	hasBases               bool
	resolving              bool
	hasOwnMembers          bool
	hasRequiredOwnMembers  bool
}

func (p *pendingInstantiatedMembers) state(i int) uint32 {
	return (p.states[i>>4] >> ((i & 15) * 2)) & 3
}

func (p *pendingInstantiatedMembers) memberAt(i int) *ast.Symbol {
	source := p.source.entries[i]
	if known := p.instantiated[source.Name]; known != nil {
		return known
	}
	if p.state(i) == pendingMemberKept {
		return source
	}
	return p.checker.newInstantiatedSymbol(source, p.mapper)
}

func (p *pendingInstantiatedMembers) ownMember(name string) *ast.Symbol {
	i, ok := p.source.positions[name]
	if !ok || p.state(i) == pendingMemberSkipped {
		return nil
	}
	if known := p.instantiated[name]; known != nil {
		return known
	}
	symbol := p.memberAt(i)
	if p.instantiated == nil {
		p.instantiated = make(ast.SymbolTable)
	}
	p.instantiated[name] = symbol
	return symbol
}

func (p *pendingInstantiatedMembers) get(name string) *ast.Symbol {
	if names := p.memberNames; names != nil {
		if i, ok := names.positions[name]; ok {
			return p.materializedProperties[i]
		}
		return nil
	}
	existing := p.ownMember(name)
	if existing != nil {
		return existing
	}
	for _, base := range p.bases {
		if existing != nil && existing.Flags&ast.SymbolFlagsValue != 0 {
			break
		}
		var inherited *ast.Symbol
		if base.typ != nil {
			if !isReservedMemberName(name) {
				inherited = getResolvedMember(base.typ, name)
				if inherited != nil && !p.checker.symbolIsValue(inherited) {
					inherited = nil
				}
			}
		} else {
			for _, symbol := range base.properties {
				if symbol.Name == name {
					inherited = symbol
					break
				}
			}
		}
		if inherited != nil && !isStaticPrivateIdentifierProperty(inherited) {
			existing = inherited
		}
	}
	return existing
}

func (p *pendingInstantiatedMembers) ownTable() ast.SymbolTable {
	table := make(ast.SymbolTable, len(p.source.entries))
	for i, source := range p.source.entries {
		state := p.state(i)
		if state == pendingMemberSkipped {
			continue
		}
		var symbol *ast.Symbol
		if p.source.positions[source.Name] == i {
			symbol = p.memberAt(i)
		} else if state == pendingMemberKept {
			symbol = source
		} else {
			// Lists can contain duplicate names. Earlier entries are instantiated in
			// their original order, but must not reuse the cached final-name symbol.
			symbol = p.checker.newInstantiatedSymbol(source, p.mapper)
		}
		table[source.Name] = symbol
	}
	return table
}

func (p *pendingInstantiatedMembers) materialize(t *StructuredType) {
	if p.memberNames != nil {
		return
	}
	if !p.resolving && p.source.lastMemberNames != nil {
		p.materializeWithLayout(t, p.source.lastMemberNames)
		return
	}
	t.pendingMembers = nil
	members := p.ownTable()
	p.instantiated = nil
	var ownProperties []*ast.Symbol
	if p.hasBases && p.resolving {
		ownProperties = p.checker.getNamedMembers(members, t.symbol)
	}
	for _, base := range p.bases {
		properties := base.properties
		if base.typ != nil {
			properties = base.typ.Properties()
		}
		members = p.checker.addInheritedMembers(members, properties)
	}
	t.members = members
	if p.hasBases && p.resolving {
		// While bases are being resolved, eager tsgo exposes own properties only.
		t.properties = ownProperties
	} else {
		t.properties = p.checker.getNamedMembers(members, t.symbol)
	}
	// Reentrant base resolution continues to mutate the table. Only completed
	// tables whose every member is a named property can be recovered from a slice.
	if !p.resolving {
		p.keepTableOnDemand(t, members)
	}
}

func (p *pendingInstantiatedMembers) keepTableOnDemand(t *StructuredType, members ast.SymbolTable) {
	properties := t.properties
	if len(properties) != len(members) {
		return
	}
	for _, symbol := range properties {
		if members[symbol.Name] != symbol {
			return
		}
	}
	names := p.source.lastMemberNames
	if !hasMemberNames(names, properties) {
		names = &memberNames{names: make([]string, len(properties)), positions: make(map[string]int, len(properties))}
		for i, symbol := range properties {
			names.names[i] = symbol.Name
			names.positions[symbol.Name] = i
		}
		p.source.lastMemberNames = names
	}
	p.keepPropertiesOnDemand(t, names, properties)
}

func (p *pendingInstantiatedMembers) keepPropertiesOnDemand(t *StructuredType, names *memberNames, properties []*ast.Symbol) {
	p.memberNames = names
	p.materializedProperties = properties
	// After complete materialization, lookups only need the shared name layout
	// and this instance's properties. Release the inference/source/base graph.
	// Keep hasBases and own-member flags for the optional-property shortcuts.
	p.checker = nil
	p.source = nil
	p.mapper = nil
	p.states = nil
	p.bases = nil
	p.instantiated = nil
	t.members = nil
	t.pendingMembers = p
}

func hasMemberNames(names *memberNames, properties []*ast.Symbol) bool {
	if names == nil || len(names.names) != len(properties) {
		return false
	}
	for i, symbol := range properties {
		if names.names[i] != symbol.Name {
			return false
		}
	}
	return true
}

func (p *pendingInstantiatedMembers) materializeTable(t *StructuredType) {
	if p.memberNames == nil {
		p.materialize(t)
		if t.pendingMembers != p {
			return
		}
	}
	members := make(ast.SymbolTable, len(p.materializedProperties))
	for _, symbol := range p.materializedProperties {
		members[symbol.Name] = symbol
	}
	t.members = members
	t.pendingMembers = nil
	p.materializedProperties = nil
	p.memberNames = nil
}

func (c *Checker) pendingInstantiatedTable(source *InterfaceType, mapper *TypeMapper) *pendingInstantiatedMembers {
	table := source.declaredMembers
	if len(table) == 0 {
		return nil
	}
	entries := source.instantiatedMemberSource
	if entries == nil {
		names := make([]string, 0, len(table))
		for name, symbol := range table {
			if name != symbol.Name {
				return nil
			}
			names = append(names, name)
		}
		slices.Sort(names)
		entries = &instantiatedMemberSource{entries: make([]*ast.Symbol, len(names)), positions: make(map[string]int, len(names))}
		for i, name := range names {
			entries.entries[i] = table[name]
			entries.positions[name] = i
		}
		source.instantiatedMemberSource = entries
	}
	p := &pendingInstantiatedMembers{checker: c, source: entries, mapper: mapper, states: make([]uint32, (len(entries.entries)+15)/16)}
	for i, symbol := range entries.entries {
		state := pendingMemberSkipped
		if c.isNamedMember(symbol, symbol.Name) {
			// An alias can be replaced by an inherited value. Keep such tables eager.
			if symbol.Flags&ast.SymbolFlagsValue == 0 {
				return nil
			}
			state = pendingMemberInstantiated
			if c.keepsSymbolUnderInstantiation(symbol, mapper) {
				state = pendingMemberKept
			}
			p.hasOwnMembers = true
			if symbol.Flags&ast.SymbolFlagsOptional == 0 {
				p.hasRequiredOwnMembers = true
			}
		}
		p.states[i>>4] |= state << ((i & 15) * 2)
	}
	if slices.Equal(source.lastMemberStates, p.states) {
		p.states = source.lastMemberStates
	} else {
		source.lastMemberStates = p.states
	}
	return p
}

func (c *Checker) pendingInstantiatedList(list []*ast.Symbol, mapper *TypeMapper) *pendingInstantiatedMembers {
	if len(list) == 0 {
		return nil
	}
	key := instantiatedMemberListKey{first: &list[0], length: len(list)}
	source := c.instantiatedMemberLists[key]
	if source == nil {
		source = &instantiatedMemberSource{entries: list, positions: make(map[string]int, len(list))}
		for i, symbol := range list {
			source.positions[symbol.Name] = i
		}
		if c.instantiatedMemberLists == nil {
			c.instantiatedMemberLists = make(map[instantiatedMemberListKey]*instantiatedMemberSource)
		}
		c.instantiatedMemberLists[key] = source
	}
	p := &pendingInstantiatedMembers{checker: c, source: source, mapper: mapper, states: make([]uint32, (len(list)+15)/16), hasOwnMembers: true}
	for i, symbol := range list {
		state := pendingMemberInstantiated
		if c.keepsSymbolUnderInstantiation(symbol, mapper) {
			state = pendingMemberKept
		}
		p.states[i>>4] |= state << ((i & 15) * 2)
		if symbol.Flags&ast.SymbolFlagsOptional == 0 {
			p.hasRequiredOwnMembers = true
		}
	}
	return p
}

func getResolvedMember(t *StructuredType, name string) *ast.Symbol {
	if p := t.pendingMembers; p != nil {
		return p.get(name)
	}
	return t.members[name]
}

func hasResolvedProperties(t *StructuredType) bool {
	if p := t.pendingMembers; p != nil && !p.resolving && p.hasOwnMembers {
		return true
	}
	return len(t.Properties()) != 0
}

func resolvedPropertiesAreOptional(t *StructuredType) bool {
	if p := t.pendingMembers; p != nil && !p.resolving {
		if p.hasRequiredOwnMembers {
			return false
		}
		if !p.hasBases {
			return true
		}
	}
	for _, symbol := range t.Properties() {
		if symbol.Flags&ast.SymbolFlagsOptional == 0 {
			return false
		}
	}
	return true
}

func (c *Checker) setPendingStructuredTypeMembers(t *Type, p *pendingInstantiatedMembers, callSignatures []*Signature, constructSignatures []*Signature, indexInfos []*IndexInfo) {
	c.setStructuredTypeMembers(t, nil, callSignatures, constructSignatures, indexInfos)
	t.AsStructuredType().pendingMembers = p
}

func (c *Checker) resolvePendingObjectTypeMembers(t *Type, p *pendingInstantiatedMembers, baseTypes []*Type, mapper *TypeMapper, typeArguments []*Type, callSignatures []*Signature, constructSignatures []*Signature, indexInfos []*IndexInfo) {
	c.setPendingStructuredTypeMembers(t, p, callSignatures, constructSignatures, indexInfos)
	if len(baseTypes) == 0 {
		return
	}
	p.hasBases = true
	p.resolving = true
	thisArgument := core.LastOrNil(typeArguments)
	t.objectFlags |= ObjectFlagsUnresolvedMembers
	for _, baseType := range baseTypes {
		instantiatedBaseType := baseType
		if thisArgument != nil {
			instantiatedBaseType = c.getTypeWithThisArgument(c.instantiateType(baseType, mapper), thisArgument, false)
		}
		var base inheritedPendingMembers
		if instantiatedBaseType.flags&TypeFlagsObject != 0 && instantiatedBaseType.objectFlags&ObjectFlagsMapped == 0 {
			resolved := c.resolveStructuredTypeMembers(instantiatedBaseType)
			if pending := resolved.pendingMembers; pending != nil && pending.memberNames == nil && !pending.resolving {
				base.typ = resolved
			}
		}
		if base.typ == nil {
			base.properties = c.getPropertiesOfType(instantiatedBaseType)
		}
		if t.AsStructuredType().pendingMembers == p {
			p.bases = append(p.bases, base)
		} else {
			properties := base.properties
			if base.typ != nil {
				properties = base.typ.Properties()
			}
			t.AsStructuredType().members = c.addInheritedMembers(t.AsStructuredType().members, properties)
		}
		callSignatures = core.Concatenate(callSignatures, c.getSignaturesOfType(instantiatedBaseType, SignatureKindCall))
		constructSignatures = core.Concatenate(constructSignatures, c.getSignaturesOfType(instantiatedBaseType, SignatureKindConstruct))
		var inheritedIndexInfos []*IndexInfo
		if instantiatedBaseType != c.anyType {
			inheritedIndexInfos = c.getIndexInfosOfType(instantiatedBaseType)
		} else {
			inheritedIndexInfos = []*IndexInfo{c.anyBaseTypeIndexInfo}
		}
		indexInfos = core.Concatenate(indexInfos, core.Filter(inheritedIndexInfos, func(info *IndexInfo) bool { return findIndexInfo(indexInfos, info.keyType) == nil }))
	}
	t.objectFlags &^= ObjectFlagsUnresolvedMembers
	p.resolving = false
	if t.AsStructuredType().pendingMembers == p {
		c.setPendingStructuredTypeMembers(t, p, callSignatures, constructSignatures, indexInfos)
	} else {
		c.setStructuredTypeMembers(t, t.AsStructuredType().members, callSignatures, constructSignatures, indexInfos)
	}
}

func (c *Checker) hasPropertiesOfType(t *Type) bool {
	t = c.getReducedApparentType(t)
	if t.flags&TypeFlagsUnionOrIntersection != 0 {
		return len(c.getPropertiesOfUnionOrIntersectionType(t)) != 0
	}
	return t.flags&TypeFlagsObject != 0 && hasResolvedProperties(c.resolveStructuredTypeMembers(t))
}
