package checker

import (
	"path/filepath"
	"testing"
)

func TestInstantiationWindowResultsAndEpoch(t *testing.T) {
	s := &instantiationWindow{slots: make([]windowEntry, 1)}
	c := &Checker{}
	input := &Type{id: 1}
	m := &TypeMapper{}
	result := &Type{id: 2}
	a := s.begin(c, input, m, nil)
	c.TotalInstantiationCount += 3
	s.finish(c, a, result)
	b := s.begin(c, input, m, nil)
	s.finish(c, b, result)
	s.epoch++
	b = s.begin(c, input, m, nil)
	s.finish(c, b, &Type{id: 3})
	if s.counts.FirstInWindow != 1 || s.counts.RepeatedCompleted != 2 || s.counts.SameObservedState != 1 || s.counts.ChangedObservedState != 1 || s.counts.SameResult != 1 || s.counts.ChangedResult != 1 || s.counts.SameStateAndResult != 1 || s.counts.FirstDescendantInstantiations != 3 {
		t.Fatalf("counts %+v", s.counts)
	}
}
func TestInstantiationWindowNestedAndEviction(t *testing.T) {
	s := &instantiationWindow{slots: make([]windowEntry, 1)}
	c := &Checker{}
	input := &Type{id: 1}
	m := &TypeMapper{}
	a := s.begin(c, input, m, nil)
	nested := s.begin(c, input, m, nil)
	s.finish(c, nested, input)
	b := s.begin(c, &Type{id: 2}, m, nil)
	s.finish(c, b, input)
	s.finish(c, a, input)
	if s.counts.Selected != 3 || s.counts.FirstInWindow != 2 || s.counts.NestedPending != 1 || s.counts.Evictions != 1 || s.counts.EvictedBeforeFinish != 1 || s.counts.FinishedFirst != 1 {
		t.Fatalf("counts %+v", s.counts)
	}
}
func TestInstantiationWindowSelectionAndOutput(t *testing.T) {
	s := &instantiationWindow{slots: make([]windowEntry, 4096), mask: 127}
	c := &Checker{}
	m := &TypeMapper{}
	for id := 1; id <= 8192; id++ {
		input := &Type{id: TypeId(id)}
		token := s.begin(c, input, m, nil)
		s.finish(c, token, input)
	}
	s.begin(c, &Type{id: 9}, m, &TypeAlias{})
	if s.counts.Aliased != 1 || s.counts.Selected == 0 || s.counts.Unsampled == 0 || s.counts.Requests != s.counts.Aliased+s.counts.Unsampled+s.counts.Selected {
		t.Fatal("selection partition")
	}
	path := filepath.Join(t.TempDir(), "counts.json")
	if err := WriteInstantiationWindowSnapshots(path, nil); err != nil {
		t.Fatal(err)
	}
	if err := WriteInstantiationWindowSnapshots(path, nil); err == nil {
		t.Fatal("overwrote output")
	}
}
