package checker

import "testing"

func densityChecker(t *testing.T) *Checker {
	t.Setenv("TSC_GO_TEMPLATE_RELATION_DENSITY", "enabled")
	return &Checker{templateRelationDensity: newTemplateRelationDensity(), assignableRelation: &Relation{}, comparableRelation: &Relation{}, identityRelation: &Relation{}, subtypeRelation: &Relation{}, strictSubtypeRelation: &Relation{}}
}
func TestTemplateDensityPacking(t *testing.T) {
	c := densityChecker(t)
	for a := TypeId(16); a < 32; a++ {
		for b := TypeId(32); b < 48; b++ {
			c.observeTemplateFailure(&Type{id: a, flags: TypeFlagsTemplateLiteral}, &Type{id: b, flags: TypeFlagsTemplateLiteral}, IntersectionStateNone, c.assignableRelation, RelationComparisonResultFailed)
		}
	}
	s, ok := c.TemplateRelationDensitySnapshot()
	r := s.Rows[0]
	if !ok || s.Tiles != 1 || r.Recorded != 256 || r.Unique != 256 || r.Occupancy[256] != 1 {
		t.Fatal(s)
	}
	// Snapshot must not mutate/accumulate histogram counts.
	again, _ := c.TemplateRelationDensitySnapshot()
	if again != s {
		t.Fatal("snapshot mutation")
	}
	if c.TypeCount != 0 || c.assignableRelation.size() != 0 {
		t.Fatal("semantic effects")
	}
}
func TestTemplateDensityCapAndResults(t *testing.T) {
	c := densityChecker(t)
	c.templateRelationDensity.limit = 1
	a, b := &Type{id: 1, flags: TypeFlagsStringLiteral}, &Type{id: 2, flags: TypeFlagsTemplateLiteral}
	c.observeTemplateFailure(a, b, 0, c.assignableRelation, RelationComparisonResultFailed)
	c.observeTemplateFailure(a, b, 0, c.assignableRelation, RelationComparisonResultFailed)
	c.observeTemplateFailure(a, b, 1, c.assignableRelation, RelationComparisonResultFailed)
	c.observeTemplateFailure(a, b, 0, c.assignableRelation, RelationComparisonResultFailed|RelationComparisonResultReportsUnreliable)
	a.id = 0
	c.observeTemplateFailure(a, b, 0, c.assignableRelation, RelationComparisonResultFailed)
	s, _ := c.TemplateRelationDensitySnapshot()
	r := s.Rows[0]
	if r.Writes != 5 || r.Recorded != 2 || r.Repeated != 1 || r.Unique != 1 || r.Dropped != 1 || r.NonPlain != 1 || r.Unpackable != 1 {
		t.Fatal(r)
	}
}
func TestTemplateDensityIdentityAndDomain(t *testing.T) {
	c := densityChecker(t)
	a, b := &Type{id: 17, flags: TypeFlagsTemplateLiteral}, &Type{id: 33, flags: TypeFlagsTemplateLiteral}
	c.observeTemplateFailure(a, b, 0, c.identityRelation, RelationComparisonResultFailed)
	c.observeTemplateFailure(b, a, 0, c.identityRelation, RelationComparisonResultFailed)
	c.observeTemplateFailure(a, b, 0, c.assignableRelation, RelationComparisonResultFailed)
	a.flags = TypeFlagsNumber
	c.observeTemplateFailure(a, b, 0, c.assignableRelation, RelationComparisonResultFailed)
	s, _ := c.TemplateRelationDensitySnapshot()
	if s.Rows[2].Unique != 1 || s.Rows[2].Repeated != 1 || s.Rows[0].Writes != 1 || s.Tiles != 2 {
		t.Fatal(s)
	}
}
