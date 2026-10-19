package checker

import "github.com/microsoft/typescript-go/internal/ast"

// A property reference is either an actual symbol or an unpublished pending
// clone. Temporary metadata never enters identity comparisons or symbol caches.
type propertyRef struct {
	symbol *ast.Symbol
	view   pendingPropertyView
}

func (p propertyRef) metadata() propertyViewMetadata {
	if p.symbol != nil {
		return metadataOfProperty(p.symbol)
	}
	return p.view.metadata()
}

func (p propertyRef) materialize() *ast.Symbol {
	if p.symbol != nil {
		return p.symbol
	}
	return p.view.materialize()
}

func (p propertyRef) existingSymbol() *ast.Symbol {
	if p.symbol != nil {
		return p.symbol
	}
	v := p.view
	if v.original == nil {
		return nil
	}
	pending := v.owner.pendingMembers
	if pending != v.pending || pending.memberNames != nil {
		return v.materialize()
	}
	if symbol := pending.instantiated[v.name]; symbol != nil {
		return symbol
	}
	if v.kept {
		return v.original
	}
	return nil
}

func samePropertyRef(a, b propertyRef) bool {
	if a.view.original != nil && b.view.original != nil && a.view.owner == b.view.owner && a.view.name == b.view.name {
		return true
	}
	x, y := a.existingSymbol(), b.existingSymbol()
	return x != nil && x == y
}

func (p propertyRef) modifierFlags() ast.ModifierFlags {
	if symbol := p.existingSymbol(); symbol != nil {
		return getDeclarationModifierFlagsFromSymbol(symbol)
	}
	m := p.metadata()
	snapshot := ast.Symbol{Flags: m.flags, CheckFlags: m.checkFlags, Parent: m.parent, ValueDeclaration: m.valueDeclaration, Declarations: p.view.original.Declarations}
	return getDeclarationModifierFlagsFromSymbol(&snapshot)
}

func (p propertyRef) nonMissingType(c *Checker) *Type {
	if p.symbol != nil {
		return c.getNonMissingTypeOfSymbol(p.symbol)
	}
	typ := p.view.typeOf(c, false)
	return c.removeMissingType(typ, p.metadata().flags&ast.SymbolFlagsOptional != 0)
}

type propertyRefSequence struct {
	symbols []*ast.Symbol
	pending pendingPropertySequence
}

func (c *Checker) propertyRefs(t *Type) propertyRefSequence {
	t = c.getReducedApparentType(t)
	if t.flags&TypeFlagsUnionOrIntersection != 0 {
		return propertyRefSequence{symbols: c.getPropertiesOfUnionOrIntersectionType(t)}
	}
	if t.flags&TypeFlagsObject == 0 {
		return propertyRefSequence{}
	}
	owner := c.resolveStructuredTypeMembers(t)
	if sequence, ok := c.pendingPropertySequence(owner); ok {
		return propertyRefSequence{pending: sequence}
	}
	return propertyRefSequence{symbols: owner.Properties()}
}

func (s propertyRefSequence) len() int {
	if s.pending.owner != nil {
		return len(s.pending.originals)
	}
	return len(s.symbols)
}

func (s propertyRefSequence) at(i int) propertyRef {
	if s.pending.owner != nil {
		return propertyRef{view: s.pending.at(i)}
	}
	return propertyRef{symbol: s.symbols[i]}
}

func (r *Relater) propertyRefsRelatedTo(source, target propertyRef, reportErrors bool, intersectionState IntersectionState) (Ternary, bool) {
	if reportErrors || r.relation == r.c.strictSubtypeRelation {
		return TernaryFalse, false
	}
	sourceFlags, targetFlags := source.modifierFlags(), target.modifierFlags()
	if (sourceFlags|targetFlags)&ast.ModifierFlagsProtected != 0 {
		return TernaryFalse, false
	}
	if (sourceFlags|targetFlags)&ast.ModifierFlagsPrivate != 0 && source.metadata().valueDeclaration != target.metadata().valueDeclaration {
		return TernaryFalse, true
	}
	targetIsOptional := r.c.strictNullChecks && target.metadata().checkFlags&ast.CheckFlagsPartial != 0
	effectiveTarget := r.c.addOptionalityEx(target.nonMissingType(r.c), false, targetIsOptional)
	related := TernaryTrue
	if effectiveTarget.flags&TypeFlagsAnyOrUnknown == 0 {
		related = r.isRelatedToEx(source.nonMissingType(r.c), effectiveTarget, RecursionFlagsBoth, false, nil, intersectionState)
	}
	if related == TernaryFalse {
		return related, true
	}
	sm, tm := source.metadata(), target.metadata()
	if r.relation != r.c.comparableRelation && sm.flags&ast.SymbolFlagsOptional != 0 && tm.flags&ast.SymbolFlagsClassMember != 0 && tm.flags&ast.SymbolFlagsOptional == 0 {
		return TernaryFalse, true
	}
	return related, true
}
