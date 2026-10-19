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
