package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/collections"
)

// Called only after the ordinary relation prechecks, for wide targets.
// Keep its filter storage out of propertiesRelatedTo's common frame.
func (r *Relater) sparsePropertiesRelatedTo(source, target *Type, reportErrors bool, excludedProperties collections.Set[string], optionalsOnly bool, intersectionState IntersectionState, properties []*ast.Symbol) Ternary {
	result := TernaryTrue
	// Wide targets often have hundreds of absent optional properties. Preserve
	// target order and refresh membership after any real lookup/comparison.
	useSparseFilter := true
	refreshSparseFilter := true
	var sparseFilter sparsePropertyFilter
	numericNamesOnly := isTupleType(source) && isTupleType(target)
	for _, targetProp := range excludeProperties(properties, excludedProperties) {
		name := targetProp.Name
		if targetProp.Flags&ast.SymbolFlagsPrototype == 0 && (!numericNamesOnly || isNumericLiteralName(name) || name == "length") && (!optionalsOnly || targetProp.Flags&ast.SymbolFlagsOptional != 0) {
			if useSparseFilter {
				if refreshSparseFilter {
					sparseFilter, useSparseFilter = r.c.newSparsePropertyFilter(source)
					refreshSparseFilter = false
				}
				if useSparseFilter && !sparseFilter.mayContain(name) {
					continue
				}
			}
			sourceProp := r.c.getPropertyOfType(source, name)
			refreshSparseFilter = true
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
