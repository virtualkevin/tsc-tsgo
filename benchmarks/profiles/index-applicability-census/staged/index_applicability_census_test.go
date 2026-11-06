package checker

import "testing"

func indexCensusTestChecker(t *testing.T) *Checker {
	t.Setenv("TSC_GO_INDEX_APPLICABILITY_CENSUS", "enabled")
	return &Checker{indexApplicabilityCensus: newIndexApplicabilityCensus(), assignableRelation: &Relation{}, identityRelation: &Relation{}, comparableRelation: &Relation{}, strictSubtypeRelation: &Relation{}}
}
func TestIndexApplicabilityNestedHistory(t *testing.T) {
	c := indexCensusTestChecker(t)
	a, b := &Type{id: 1, flags: TypeFlagsString}, &Type{id: 2, flags: TypeFlagsNumber}
	outer := c.beginIndexApplicability(a, b)
	c.TotalInstantiationCount += 2
	inner := c.beginIndexApplicability(a, b)
	c.TotalInstantiationCount += 3
	c.endIndexApplicability(inner, false)
	c.TotalInstantiationCount += 4
	c.endIndexApplicability(outer, true)
	s, ok := c.IndexApplicabilitySnapshot()
	if !ok || s.Active || s.TrackedPairs != 1 || len(s.Rows) != 1 {
		t.Fatal(s)
	}
	r := s.Rows[0]
	if r.Calls != 2 || r.TrackedFirst != 1 || r.TrackedRepeat != 1 || r.ChangedResult != 1 || r.InclusiveInstantiations != 12 || r.ExclusiveInstantiations != 9 || r.RepeatExclusiveInstantiations != 6 {
		t.Fatal(r)
	}
}
func TestIndexApplicabilityCapAndEffects(t *testing.T) {
	c := indexCensusTestChecker(t)
	c.indexApplicabilityCensus.limit = 1
	a, b, d := &Type{id: 1}, &Type{id: 2}, &Type{id: 3}
	for _, p := range [][2]*Type{{a, b}, {a, d}, {a, b}} {
		f := c.beginIndexApplicability(p[0], p[1])
		c.endIndexApplicability(f, false)
	}
	s, _ := c.IndexApplicabilitySnapshot()
	r := s.Rows[0]
	if r.Calls != 3 || r.TrackedFirst != 1 || r.TrackedRepeat != 1 || r.Dropped != 1 {
		t.Fatal(r)
	}
	// Size changes are recorded, including negative deltas; replacements are not.
	f := c.beginIndexApplicability(a, b)
	c.assignableRelation.results = make(map[CacheHashKey]RelationComparisonResult)
	c.assignableRelation.results[CacheHashKey{}] = RelationComparisonResultSucceeded
	c.endIndexApplicability(f, true)
	s, _ = c.IndexApplicabilitySnapshot()
	if s.Rows[0].ExclusiveRelationGrowth != 1 {
		t.Fatal(s)
	}
}
func TestIndexApplicabilityPrimitiveDifferential(t *testing.T) {
	for _, enabled := range []bool{false, true} {
		c := indexCensusTestChecker(t)
		if !enabled {
			c.indexApplicabilityCensus = nil
		}
		c.stringType = &Type{id: 1, flags: TypeFlagsString}
		c.numberType = &Type{id: 2, flags: TypeFlagsNumber}
		for _, p := range []struct {
			s, t *Type
			want bool
		}{{c.stringType, c.stringType, true}, {c.numberType, c.stringType, true}, {c.stringType, c.numberType, false}, {c.numberType, c.numberType, true}} {
			if got := c.isApplicableIndexType(p.s, p.t); got != p.want {
				t.Fatal(got, p.want)
			}
		}
		if c.TotalInstantiationCount != 0 || c.assignableRelation.size() != 0 {
			t.Fatal("unexpected effects")
		}
		if enabled {
			s, _ := c.IndexApplicabilitySnapshot()
			var calls uint64
			for _, r := range s.Rows {
				calls += r.Calls
			}
			if calls != 4 || s.Active {
				t.Fatal(s)
			}
		}
	}
}
