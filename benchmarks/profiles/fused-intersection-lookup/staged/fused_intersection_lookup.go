package checker

import "github.com/microsoft/typescript-go/internal/ast"

// cachedIntersectionProperty recognizes an already completed identity path through
// getReducedApparentType and the non-augmented property cache. It does not resolve
// anything or retain a result across calls. The caller still queries the symbol's
// current type, including any lazy resolution and effects of that query.
func cachedIntersectionProperty(t *Type, name string) *ast.Symbol {
	if t.flags != TypeFlagsIntersection || t.objectFlags&(ObjectFlagsMapped|ObjectFlagsIsNeverIntersectionComputed|ObjectFlagsIsNeverIntersection) != ObjectFlagsIsNeverIntersectionComputed {
		return nil
	}
	d := t.AsIntersectionType()
	if d.resolvedApparentType != t {
		return nil
	}
	prop := d.propertyCacheWithoutFunctionPropertyAugment[name]
	if prop != nil && prop.CheckFlags&ast.CheckFlagsReadPartial == 0 {
		return prop
	}
	return nil
}
