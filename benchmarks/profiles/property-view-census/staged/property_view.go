package checker

import "github.com/microsoft/typescript-go/internal/ast"

// Experimental own-member view. Does not change production property consumers.
// Metadata reads must not run type queries or revise frozen keep/clone state.
type pendingPropertyView struct {
	owner    *StructuredType
	pending  *pendingInstantiatedMembers
	original *ast.Symbol
	name     string
	kept     bool
}
type propertyViewMetadata struct {
	name             string
	flags            ast.SymbolFlags
	checkFlags       ast.CheckFlags
	parent           *ast.Symbol
	valueDeclaration *ast.Node
}

// supported=false requires the old consumer, before any materialization effects.
// A nil original with supported=true denotes a missing own property.
func lookupPendingPropertyView(owner *StructuredType, name string) (pendingPropertyView, bool) {
	p := owner.pendingMembers
	if p == nil || p.memberNames != nil || p.resolving || p.hasBases || len(p.bases) != 0 || p.source == nil {
		return pendingPropertyView{}, false
	}
	// A duplicate source list has observable earlier-entry clone behavior.
	if len(p.source.entries) != len(p.source.positions) {
		return pendingPropertyView{}, false
	}
	i, ok := p.source.positions[name]
	if !ok || p.state(i) == pendingMemberSkipped {
		return pendingPropertyView{owner: owner, name: name}, true
	}
	original := p.source.entries[i]
	if original.Name != name || original.Flags&ast.SymbolFlagsProperty == 0 || original.CheckFlags&ast.CheckFlagsInstantiated != 0 {
		return pendingPropertyView{}, false
	}
	return pendingPropertyView{owner, p, original, name, p.state(i) == pendingMemberKept}, true
}
func metadataOfProperty(symbol *ast.Symbol) propertyViewMetadata {
	if symbol == nil {
		return propertyViewMetadata{}
	}
	return propertyViewMetadata{symbol.Name, symbol.Flags, symbol.CheckFlags, symbol.Parent, symbol.ValueDeclaration}
}
func (v pendingPropertyView) metadata() propertyViewMetadata {
	if v.original == nil {
		return propertyViewMetadata{}
	}
	p := v.owner.pendingMembers
	if p != v.pending || p.memberNames != nil {
		return metadataOfProperty(getResolvedMember(v.owner, v.name))
	}
	if symbol := p.instantiated[v.name]; symbol != nil {
		return metadataOfProperty(symbol)
	}
	result := metadataOfProperty(v.original)
	if !v.kept {
		result.flags |= ast.SymbolFlagsTransient
		result.checkFlags = ast.CheckFlagsInstantiated | result.checkFlags&(ast.CheckFlagsReadonly|ast.CheckFlagsLate|ast.CheckFlagsOptionalParameter|ast.CheckFlagsRestParameter)
	}
	return result
}
func (v pendingPropertyView) materialize() *ast.Symbol {
	if v.original == nil {
		return nil
	}
	// Use the owner, not the saved pending object: materialization can retire and
	// clear the pending object's source graph while API results remain alive.
	return getResolvedMember(v.owner, v.name)
}

// One pending clone's type caches, not a cross-property instantiation cache.
// Once materialized, the actual symbol links are authoritative. In-flight
// queries retain this typed entry even if enumeration retires the pending map.
type pendingPropertyType struct {
	resolvedType *Type
	nameType     *Type
	symbol       *ast.Symbol
}

func (v pendingPropertyView) typeOf(c *Checker, write bool) *Type {
	c.countPropertyView(5)
	if write {
		c.countPropertyView(18)
	}
	query := c.getTypeOfSymbol
	if write {
		query = c.getWriteTypeOfSymbol
	}
	if v.original == nil {
		return nil
	}
	p := v.owner.pendingMembers
	if p != v.pending || p.memberNames != nil {
		c.countPropertyView(6)
		return query(v.materialize())
	}
	if symbol := p.instantiated[v.name]; symbol != nil {
		c.countPropertyView(6)
		return query(symbol)
	}
	if v.kept {
		c.countPropertyView(7)
		return query(v.original)
	}
	if write {
		return c.removeMissingType(v.typeOf(c, false), v.metadata().flags&ast.SymbolFlagsOptional != 0)
	}
	state := v.prepareTypeState(c)
	cached := state.resolvedType
	if cached != nil {
		c.countPropertyView(8)
		return cached
	}
	// Capture the mapper before source evaluation can retire the pending owner.
	c.countPropertyView(9)
	mapper := p.mapper
	result := c.instantiateType(c.getTypeOfSymbol(v.original), mapper)
	state.resolvedType = result
	// Reentrant enumeration may have published the symbol while computing result.
	// Match the original outer assignment even if an inner query filled the cache.
	if state.symbol != nil {
		links := c.valueSymbolLinks.Get(state.symbol)
		links.resolvedType = result
	}
	return result
}

// Capture clone metadata at the first logical property lookup, before subsequent
// target type queries can mutate the source links. Kept/materialized symbols
// already have their original behavior and need no new pending entry.
func (v pendingPropertyView) prepareTypeState(c *Checker) *pendingPropertyType {
	p := v.owner.pendingMembers
	if v.kept || p != v.pending || p.memberNames != nil || p.instantiated[v.name] != nil {
		return nil
	}
	state := p.viewTypes[v.name]
	if state == nil {
		// The ordinary clone captures nameType before any source type query.
		c.countPropertyView(3)
		state = &pendingPropertyType{nameType: c.valueSymbolLinks.Get(v.original).nameType}
		if p.viewTypes == nil {
			p.viewTypes = make(map[string]*pendingPropertyType)
		}
		p.viewTypes[v.name] = state
	}
	if state != nil {
		c.countPropertyView(4)
	}
	return state
}
