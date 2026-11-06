package checker

import (
	"os"
	"path/filepath"
	"testing"
)

func queryCensusChecker(t *testing.T) *Checker {
	t.Setenv("TSC_GO_DISCRIMINANT_QUERY_CENSUS", "enabled")
	return &Checker{discriminantQueryCensus: newDiscriminantQueryCensus(), assignableRelation: &Relation{}, subtypeRelation: &Relation{}}
}
func TestDiscriminantQueryNestedCompletion(t *testing.T) {
	c := queryCensusChecker(t)
	typ := &Type{id: 1}
	outer := c.beginDiscriminantQuery(typ, "x", &TypeDiscriminator{})
	c.TotalInstantiationCount += 2
	inner := c.beginDiscriminantQuery(typ, "x", &TypeDiscriminator{})
	c.TotalInstantiationCount += 3
	c.endDiscriminantQuery(inner, typ)
	c.TotalInstantiationCount += 4
	c.endDiscriminantQuery(outer, &Type{id: 2})
	s, _ := c.DiscriminantQuerySnapshot()
	r := s.Rows[0]
	if s.Active || s.TrackedRequests != 1 || r.Calls != 2 || r.TrackedFirst != 1 || r.TrackedRepeat != 1 || r.ChangedResult != 1 || r.Inclusive[0] != 12 || r.Exclusive[0] != 9 || r.RepeatExclusive[0] != 6 {
		t.Fatal(s)
	}
}
func TestDiscriminantQueryKeyCapAndNil(t *testing.T) {
	c := queryCensusChecker(t)
	c.discriminantQueryCensus.limit = 2
	typ := &Type{id: 1}
	for _, x := range []struct {
		typ    *Type
		name   string
		result *Type
	}{{typ, "x", nil}, {typ, "y", typ}, {typ, "x", &Type{id: 0}}, {&Type{id: 2}, "x", typ}} {
		f := c.beginDiscriminantQuery(x.typ, x.name, &ObjectLiteralDiscriminator{})
		c.endDiscriminantQuery(f, x.result)
	}
	s, _ := c.DiscriminantQuerySnapshot()
	r := s.Rows[0]
	if s.TrackedRequests != 2 || r.TrackedFirst != 2 || r.TrackedRepeat != 1 || r.Dropped != 1 || r.ChangedResult != 1 || r.NonNil != 3 {
		t.Fatal(s)
	}
}
func TestDiscriminantQueryExclusiveOutput(t *testing.T) {
	c := queryCensusChecker(t)
	s, _ := c.DiscriminantQuerySnapshot()
	p := filepath.Join(t.TempDir(), "report.json")
	if err := WriteDiscriminantQuerySnapshots(p, []DiscriminantQuerySnapshot{s}); err != nil {
		t.Fatal(err)
	}
	before, err := os.ReadFile(p)
	if err != nil {
		t.Fatal(err)
	}
	if WriteDiscriminantQuerySnapshots(p, nil) == nil {
		t.Fatal("overwrote existing report")
	}
	after, _ := os.ReadFile(p)
	if string(before) != string(after) {
		t.Fatal("report changed")
	}
	t.Setenv("TSC_GO_DISCRIMINANT_QUERY_CENSUS", "")
	if newDiscriminantQueryCensus() != nil {
		t.Fatal("disabled observer allocated")
	}
}
