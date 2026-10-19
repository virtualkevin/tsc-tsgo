package checker

import "testing"

func TestPropertyViewPresenceSnapshot(t *testing.T) {
	for _, views := range []bool{false, true} {
		c, owner, original, _ := viewFixture()
		first := &Type{flags: TypeFlagsString}
		later := &Type{flags: TypeFlagsNumber}
		links := c.valueSymbolLinks.Get(original)
		links.nameType = first
		links.resolvedType = first
		view := pendingPropertyView{}
		var resultName *Type
		if views {
			view, _ = c.propertyViewOrSymbol(&owner.Type, "clone")
			if view.original == nil {
				t.Fatal("view setup")
			}
			links.nameType = later
			view.typeOf(c, false)
			resultName = c.valueSymbolLinks.Get(view.materialize()).nameType
		} else {
			materialized := c.getPropertyOfType(&owner.Type, "clone")
			links.nameType = later
			c.getTypeOfSymbol(materialized)
			resultName = c.valueSymbolLinks.Get(materialized).nameType
		}
		if resultName != first {
			t.Errorf("views=%v: presence snapshot changed before type query", views)
		}
	}
}
