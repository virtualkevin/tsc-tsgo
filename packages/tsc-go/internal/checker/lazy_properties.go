package checker

import (
	"slices"

	"github.com/microsoft/typescript-go/internal/ast"
)

// Ports tsc-ts 0d434007d9c2180898b6c0e279caf842a6ca403f. Only properties
// combined from different constituents, with a literal or private property,
// can reduce an intersection to never. Avoid enumerating the most expensive
// constituent, and create synthetic properties only for those candidate names.
func (c *Checker) hasNeverReducedProperty(t *Type) bool {
	if resolved := t.AsIntersectionType().resolvedProperties; resolved != nil {
		for _, prop := range resolved {
			if c.isNeverReducedProperty(prop) {
				return true
			}
		}
		return false
	}
	skipped := c.getCostliestConstituent(t)
	byName := make(map[string][]*ast.Symbol)
	var names []string
	for _, current := range t.Types() {
		if current == skipped {
			continue
		}
		for _, prop := range c.getPropertiesOfType(current) {
			props, seen := byName[prop.Name]
			if !seen {
				names = append(names, prop.Name)
			}
			if !slices.Contains(props, prop) {
				byName[prop.Name] = append(props, prop)
			}
		}
	}
	var skippedType *Type
	if skipped != nil {
		skippedType = c.getApparentType(skipped)
		if c.isErrorType(skippedType) || skippedType.flags&TypeFlagsNever != 0 {
			skippedType = nil
		}
	}
	// Preserve TypeScript Map insertion order. Iterating byName directly would
	// make property resolution and recursive side effects depend on Go map order.
	for _, name := range names {
		props := byName[name]
		if skippedType != nil {
			prop := c.getPropertyOfTypeEx(skippedType, name, true, false)
			if prop != nil && !slices.Contains(props, prop) {
				props = append(props, prop)
			}
		}
		if len(props) < 2 || !c.someLiteralOrPrivateProperty(props) {
			continue
		}
		combined := c.getPropertyOfUnionOrIntersectionType(t, name, true)
		if combined != nil && c.isNeverReducedProperty(combined) {
			return true
		}
	}
	return false
}

func (c *Checker) someLiteralOrPrivateProperty(props []*ast.Symbol) bool {
	for _, prop := range props {
		if getDeclarationModifierFlagsFromSymbol(prop)&ast.ModifierFlagsPrivate != 0 {
			return true
		}
		t := c.getTypeOfSymbol(prop)
		if isLiteralType(t) || c.isPatternLiteralType(t) {
			return true
		}
	}
	return false
}

func (p *pendingInstantiatedMembers) unmaterializedMemberCount() (int, bool) {
	if p == nil || p.memberNames != nil {
		return 0, false
	}
	return len(p.source.positions), true
}

func (c *Checker) getCostliestConstituent(t *Type) *Type {
	var costliest *Type
	costliestPending, costliestProperties := 0, 0
	for _, current := range t.Types() {
		apparent := c.getReducedApparentType(current)
		if apparent.flags&TypeFlagsObject == 0 {
			continue
		}
		resolved := c.resolveStructuredTypeMembers(apparent)
		if count, pending := resolved.pendingMembers.unmaterializedMemberCount(); pending {
			if count > costliestPending {
				costliest, costliestPending = current, count
			}
		} else if costliestPending == 0 && len(resolved.properties) > costliestProperties {
			costliest, costliestProperties = current, len(resolved.properties)
		}
	}
	return costliest
}

// Ports tsc-ts e419e41ef285638402e7ba6a46c3474de190cb60. This boolean
// predicate considers required names in constituent order, without synthesizing
// every property of an unresolved union/intersection. Diagnostic-producing
// getUnmatchedProperty still uses the original full enumeration order.
func (c *Checker) hasUnmatchedProperty(source *Type, target *Type, matchDiscriminantProperties bool) bool {
	t := c.getReducedApparentType(target)
	if t.flags&TypeFlagsUnionOrIntersection == 0 || t.AsUnionOrIntersectionType().resolvedProperties != nil {
		return c.getUnmatchedProperty(source, target, false, matchDiscriminantProperties) != nil
	}
	isUnion := t.flags&TypeFlagsUnion != 0
	checked := make(map[string]bool)
	for _, current := range t.Types() {
		for _, prop := range c.getPropertiesOfType(current) {
			name := prop.Name
			if prop.Flags&ast.SymbolFlagsOptional != 0 {
				if isUnion {
					checked[name] = true
				}
				continue
			}
			if checked[name] {
				continue
			}
			checked[name] = true
			if isUnion && c.getPropertyOfType(source, name) != nil &&
				(!matchDiscriminantProperties || c.getTypeOfSymbol(prop).flags&(TypeFlagsUnit|TypeFlagsNever) == 0) {
				continue
			}
			combined := c.getPropertyOfUnionOrIntersectionType(t, name, !isUnion)
			if combined != nil && c.isUnmatchedProperty(source, combined, false, matchDiscriminantProperties) {
				return true
			}
		}
		if isUnion && len(c.getIndexInfosOfType(current)) == 0 {
			break
		}
	}
	return false
}
