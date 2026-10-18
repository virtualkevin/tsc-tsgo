package checker

import "github.com/microsoft/typescript-go/internal/ast"

func sparsePropertyMembers(t *Type, limit int) (ast.SymbolTable, bool) {
	if t == nil || t.flags != TypeFlagsObject || t.objectFlags&ObjectFlagsMapped != 0 ||
		t.objectFlags&ObjectFlagsMembersResolved == 0 || t.objectFlags&ObjectFlagsUnresolvedMembers != 0 {
		return nil, false
	}
	d := t.AsStructuredType()
	if d.pendingMembers != nil || len(d.signatures) != 0 || len(d.members) > limit ||
		t.symbol != nil && t.symbol.Flags&ast.SymbolFlagsValueModule != 0 {
		return nil, false
	}
	return d.members, true
}

// Reuse only a layout already authoritative for this exact property snapshot.
// No index is created over externally exposed property slices.
func indexedPropertyLayout(target *Type, properties []*ast.Symbol) *memberNames {
	if target.flags != TypeFlagsObject || target.objectFlags&ObjectFlagsMapped != 0 || len(properties) == 0 {
		return nil
	}
	p := target.AsStructuredType().pendingMembers
	if p == nil || p.memberNames == nil || len(p.memberNames.names) != len(properties) || len(p.materializedProperties) != len(properties) || &p.materializedProperties[0] != &properties[0] {
		return nil
	}
	return p.memberNames
}

// Select the next possible hit in original target order. Repeating selection
// after every lookup/comparison observes mutations without a persistent cache.
func (c *Checker) nextIndexedProperty(source *Type, layout *memberNames, cursor int) (int, bool) {
	if source == c.anyFunctionType {
		return cursor, false
	}
	own, ok := sparsePropertyMembers(source, 7)
	if !ok {
		return cursor, false
	}
	global, ok := sparsePropertyMembers(c.globalObjectType, 32)
	if !ok {
		return cursor, false
	}
	next := len(layout.names)
	for name := range own {
		if i, found := layout.positions[name]; found && i >= cursor && i < next {
			next = i
		}
	}
	for name := range global {
		if i, found := layout.positions[name]; found && i >= cursor && i < next {
			next = i
		}
	}
	return next, true
}

// The caller has completed all relation prechecks and has no excluded properties.
func (r *Relater) indexedPropertiesRelatedTo(source, target *Type, reportErrors, optionalsOnly bool, intersectionState IntersectionState, properties []*ast.Symbol) Ternary {
	result := TernaryTrue
	layout := indexedPropertyLayout(target, properties)
	numericNamesOnly := isTupleType(source) && isTupleType(target)
	for cursor := 0; cursor < len(properties); {
		if layout != nil {
			next, ok := r.c.nextIndexedProperty(source, layout, cursor)
			if ok {
				cursor = next
			} else {
				layout = nil
			}
			if cursor == len(properties) {
				break
			}
		}
		targetProp := properties[cursor]
		cursor++
		name := targetProp.Name
		if targetProp.Flags&ast.SymbolFlagsPrototype == 0 && (!numericNamesOnly || isNumericLiteralName(name) || name == "length") && (!optionalsOnly || targetProp.Flags&ast.SymbolFlagsOptional != 0) {
			sourceProp := r.c.getPropertyOfType(source, name)
			if sourceProp != nil && sourceProp != targetProp {
				related := r.propertyRelatedTo(source, target, sourceProp, targetProp, r.c.getNonMissingTypeOfSymbol, reportErrors, intersectionState, r.relation == r.c.comparableRelation)
				if related == TernaryFalse {
					return TernaryFalse
				}
				result &= related
			}
		}
	}
	return result
}
