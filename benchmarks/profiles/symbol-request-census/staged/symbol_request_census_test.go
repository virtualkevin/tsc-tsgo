package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"path/filepath"
	"testing"
)

func TestSymbolRequestStateAndCapacity(t *testing.T) {
	s := &symbolRequestCensus{entries: make(map[symbolRequestKey]symbolRequestState), limit: 1}
	symbol := &ast.Symbol{}
	other := &ast.Symbol{}
	links := &ValueSymbolLinks{}
	s.observe(symbol, nil, links)
	s.observe(symbol, nil, links)
	links.resolvedType = &Type{}
	s.observe(symbol, nil, links)
	s.observe(other, nil, links)
	s.observe(symbol, nil, links)
	want := SymbolRequestCounts{Requests: 5, NewKeys: 1, RepeatedSameObservedState: 2, RepeatedChangedObservedState: 1, UntrackedAtCapacity: 1}
	if s.counts[0] != want || len(s.entries) != 1 {
		t.Fatalf("got %+v", s.counts)
	}
}
func TestSymbolRequestMapperKinds(t *testing.T) {
	s := &symbolRequestCensus{entries: make(map[symbolRequestKey]symbolRequestState), limit: 8}
	symbol := &ast.Symbol{}
	links := &ValueSymbolLinks{}
	a := &Type{}
	b := &Type{}
	m := newSimpleTypeMapper(a, b)
	s.observe(symbol, m, links)
	s.observe(symbol, m, links)
	s.observe(symbol, newSimpleTypeMapper(a, b), links)
	if s.counts[1].Requests != 3 || s.counts[1].NewKeys != 2 || s.counts[1].RepeatedSameObservedState != 1 {
		t.Fatalf("got %+v", s.counts)
	}
}
func TestSymbolRequestExclusiveOutput(t *testing.T) {
	path := filepath.Join(t.TempDir(), "census.json")
	if err := WriteSymbolRequestSnapshots(path, nil); err != nil {
		t.Fatal(err)
	}
	before, _ := os.ReadFile(path)
	if err := WriteSymbolRequestSnapshots(path, nil); err == nil {
		t.Fatal("overwrote existing output")
	}
	after, _ := os.ReadFile(path)
	if string(before) != string(after) {
		t.Fatal("changed evidence")
	}
}
